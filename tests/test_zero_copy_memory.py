import os
import unittest
import numpy as np
import time
from solomon_hardware.zero_copy_memory import ZeroCopyMemorySubstrate

class TestZeroCopyMemory(unittest.TestCase):
    def setUp(self):
        self.filepath = "test_memory.bin"
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        self.substrate = ZeroCopyMemorySubstrate(self.filepath, max_records=100)

    def tearDown(self):
        self.substrate.close()
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_initialization(self):
        self.assertEqual(self.substrate.num_records, 0)
        self.assertEqual(self.substrate.mapped_max_records, 100)

    def test_add_and_get_record(self):
        record_id = 1001
        valence = 0.8
        arousal = -0.2
        concept_hash = 123456789
        embedding = np.random.rand(128).astype(np.float32)

        idx = self.substrate.add_record(record_id, valence, arousal, concept_hash, embedding)
        self.assertEqual(idx, 0)
        self.assertEqual(self.substrate.num_records, 1)

        retrieved = self.substrate.get_record(idx)
        self.assertEqual(retrieved["id"], record_id)
        self.assertAlmostEqual(retrieved["valence"], valence, places=4)
        self.assertAlmostEqual(retrieved["arousal"], arousal, places=4)
        self.assertEqual(retrieved["concept_hash"], concept_hash)

        # For 1-bit quantization, we check if the sign matches.
        orig_signs = (embedding > 0).astype(np.float32)
        retrieved_signs = (retrieved["embedding"] > 0).astype(np.float32)
        np.testing.assert_array_equal(orig_signs, retrieved_signs)

    def test_zero_copy_embeddings_matrix(self):
        # Add a few records
        embeddings = []
        for i in range(5):
            emb = np.random.rand(128).astype(np.float32)
            embeddings.append(emb)
            self.substrate.add_record(i, 0.5, 0.5, i*100, emb)

        matrix = self.substrate.get_raw_embeddings_matrix()
        self.assertEqual(matrix.shape, (5, 16)) # 16 bytes = 128 bits

        # Verify cache-line optimization and dimensions for binary quantization
        self.assertEqual(matrix.dtype, np.uint8)
        self.assertEqual(self.substrate.RECORD_SIZE, 64) # 1 * 64 cache line

    def test_search_similar(self):
        # Add target
        # For 1-bit quantization, we need a strong signal to survive the extreme lossiness
        target_emb = np.ones(128, dtype=np.float32)
        self.substrate.add_record(1, 0.5, 0.5, 100, target_emb)

        # Add noise (opposite signal)
        for i in range(10):
            noise_emb = -np.ones(128, dtype=np.float32)
            self.substrate.add_record(i+2, 0.1, 0.1, 200, noise_emb)

        # Search
        results = self.substrate.search_similar(target_emb, top_k=3)
        self.assertTrue(len(results) > 0)
        # Target should be the best match
        self.assertEqual(results[0]["record"]["id"], 1)
        self.assertTrue(results[0]["similarity"] > 0)

    def test_performance(self):
        """Test how fast we can write and read - pushing boundaries"""
        start_write = time.time()
        batch_size = 100
        for i in range(batch_size):
            emb = np.random.rand(128).astype(np.float32)
            self.substrate.add_record(i, 0.0, 0.0, i, emb)
        write_time = time.time() - start_write

        start_read = time.time()
        _ = self.substrate.get_raw_embeddings_matrix()
        read_time = time.time() - start_read

        # We expect this to be virtually instant for 100 records
        self.assertTrue(read_time < 0.1, f"Zero-copy read took too long: {read_time}s")
        print(f"\n[Performance] Wrote {batch_size} records in {write_time:.4f}s")
        print(f"[Performance] Zero-copy matrix read in {read_time:.8f}s")

if __name__ == '__main__':
    unittest.main()
