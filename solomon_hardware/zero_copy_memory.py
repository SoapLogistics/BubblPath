import os
import mmap
import struct
import numpy as np
import time

class ZeroCopyMemorySubstrate:
    """
    Zero-Copy Memory Substrate (Hardware Layer)

    Instead of parsing JSON, this utilizes memory-mapped files (mmap) and
    fixed-size binary schemas. This allows the system to read raw memory bytes
    instantly (O(1) access), providing "zero-copy" retrieval which is highly
    efficient and viable for severely constrained hardware.
    """

    # Header format: [magic_bytes: 4s] [version: I] [num_records: Q] [max_records: Q]
    # '4s I Q Q' -> 4 + 4 + 8 + 8 = 24 bytes
    HEADER_FORMAT = '<4sIQQ'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAGIC = b'ZCM1'
    VERSION = 1

    # Record format:
    # [id: Q (8)] [timestamp: Q (8)] [valence: f (4)] [arousal: f (4)]
    # [concept_hash: Q (8)] [embedding: 128f (512)]
    # Total: 32 + 512 = 544 bytes
    EMBEDDING_DIM = 128
    RECORD_FORMAT = f'<QQffQ{EMBEDDING_DIM}f'
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    def __init__(self, filepath, max_records=10000):
        self.filepath = filepath
        self.max_records = max_records
        self.file_obj = None
        self.mmap_obj = None
        self._initialize_file()

    def _initialize_file(self):
        """Initializes the memory-mapped file."""
        file_exists = os.path.exists(self.filepath)
        expected_size = self.HEADER_SIZE + (self.max_records * self.RECORD_SIZE)

        if not file_exists:
            # Create file with expected size
            with open(self.filepath, 'wb') as f:
                f.write(b'\0' * expected_size)

            # Write initial header
            with open(self.filepath, 'r+b') as f:
                header = struct.pack(self.HEADER_FORMAT, self.MAGIC, self.VERSION, 0, self.max_records)
                f.write(header)

        else:
            # Check file size, if too small, expand it.
            actual_size = os.path.getsize(self.filepath)
            if actual_size < expected_size:
                with open(self.filepath, 'a+b') as f:
                    f.truncate(expected_size)

        self.file_obj = open(self.filepath, 'r+b')
        self.mmap_obj = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_WRITE)

        # Verify Magic
        magic, version, self.num_records, self.mapped_max_records = struct.unpack_from(self.HEADER_FORMAT, self.mmap_obj, 0)
        if magic != self.MAGIC:
            raise ValueError("Invalid memory file format. Magic bytes mismatch.")

    def close(self):
        """Closes the memory mapped file."""
        if self.mmap_obj:
            self.mmap_obj.close()
        if self.file_obj:
            self.file_obj.close()

    def add_record(self, record_id, valence, arousal, concept_hash, embedding):
        """
        Adds a new record to the memory substrate.
        embedding: array-like of 128 floats.
        """
        if len(embedding) != self.EMBEDDING_DIM:
            raise ValueError(f"Embedding must be of dimension {self.EMBEDDING_DIM}")

        if self.num_records >= self.mapped_max_records:
            raise MemoryError("Zero copy memory substrate is full. Increase max_records.")

        timestamp = int(time.time() * 1000)

        offset = self.HEADER_SIZE + (self.num_records * self.RECORD_SIZE)

        # Prepare data
        # *embedding unpacks the 128 floats
        struct.pack_into(self.RECORD_FORMAT, self.mmap_obj, offset,
                         record_id, timestamp, valence, arousal, concept_hash, *embedding)

        self.num_records += 1

        # Update header
        struct.pack_into(self.HEADER_FORMAT, self.mmap_obj, 0,
                         self.MAGIC, self.VERSION, self.num_records, self.mapped_max_records)

        return self.num_records - 1 # return index

    def get_record(self, index):
        """
        Retrieves a record in O(1) time utilizing zero-copy struct unpacking.
        """
        if index < 0 or index >= self.num_records:
            raise IndexError("Record index out of bounds")

        offset = self.HEADER_SIZE + (index * self.RECORD_SIZE)
        data = struct.unpack_from(self.RECORD_FORMAT, self.mmap_obj, offset)

        return {
            "id": data[0],
            "timestamp": data[1],
            "valence": data[2],
            "arousal": data[3],
            "concept_hash": data[4],
            "embedding": np.array(data[5:], dtype=np.float32)
        }

    def get_raw_embeddings_matrix(self):
        """
        Returns a zero-copy NumPy view of all embeddings currently in memory.
        No data is copied! Super efficient for vector search.
        """
        if self.num_records == 0:
            return np.empty((0, self.EMBEDDING_DIM), dtype=np.float32)

        # The stride between embeddings is the RECORD_SIZE
        # We need to construct a structured array or use strides directly.
        # It's cleaner to read it via an ndarray buffer using offset.

        # Define a numpy dtype that matches our struct
        # We explicitly use little-endian formats to match the '<' in struct format
        record_dtype = np.dtype([
            ('id', '<u8'),
            ('timestamp', '<u8'),
            ('valence', '<f4'),
            ('arousal', '<f4'),
            ('concept_hash', '<u8'),
            ('embedding', '<f4', (self.EMBEDDING_DIM,))
        ])

        # Read directly from mmap as a numpy array, without copying!
        records_array = np.ndarray(
            shape=(self.num_records,),
            dtype=record_dtype,
            buffer=self.mmap_obj,
            offset=self.HEADER_SIZE,
            strides=(self.RECORD_SIZE,)
        )

        return records_array['embedding']

    def search_similar(self, query_embedding, top_k=5):
        """
        Demonstrates extreme efficiency using zero-copy matrix multiplication
        for cosine similarity.
        """
        if self.num_records == 0:
            return []

        embeddings = self.get_raw_embeddings_matrix()

        # Normalize query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            query_normalized = query_embedding
        else:
            query_normalized = query_embedding / query_norm

        # Normalize embeddings in memory (or assume they are normalized)
        # For speed, we just do dot product (cosine similarity if normalized)
        # To be safe, let's normalize the slice (this creates a copy for norms, but matrix mult is fast)
        norms = np.linalg.norm(embeddings, axis=1)
        norms[norms == 0] = 1 # prevent division by zero

        similarities = np.dot(embeddings, query_normalized) / norms

        # Get top k indices
        k = min(top_k, self.num_records)
        # argpartition is O(N) instead of O(N log N)
        top_indices = np.argpartition(similarities, -k)[-k:]
        # sort them descending
        top_indices = top_indices[np.argsort(-similarities[top_indices])]

        results = []
        for idx in top_indices:
            results.append({
                "index": int(idx),
                "similarity": float(similarities[idx]),
                "record": self.get_record(idx)
            })

        return results
