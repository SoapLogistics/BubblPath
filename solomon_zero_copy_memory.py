import mmap
import struct
import os

class ZeroCopyMemorySubstrate:
    """
    Path 1: The Zero-Copy Memory Substrate
    Moves Gabriel away from JSON to raw binary memory-mapped files (mmap).
    Provides instant, zero-deserialization-cost retrieval for constrained hardware.
    """
    def __init__(self, filename="gabriel_binary_memory.bin"):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "wb") as f:
                # Pre-allocate 1MB of null bytes for the memory-map
                f.write(b'\x00' * (1024 * 1024))

    def write_heuristic(self, confidence, concept_id):
        """
        Writes a highly compressed heuristic straight to binary.
        Format: [float32 confidence] [uint32 concept_id]
        """
        with open(self.filename, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            # Find the first null byte block to write to (naive allocator)
            for i in range(0, len(mm), 8):
                if mm[i:i+8] == b'\x00' * 8:
                    mm[i:i+8] = struct.pack('fI', confidence, concept_id)
                    mm.flush()
                    break
            mm.close()

    def read_heuristics(self):
        """
        Reads heuristics instantly without JSON parsing overhead.
        """
        results = []
        with open(self.filename, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            for i in range(0, len(mm), 8):
                block = mm[i:i+8]
                if block == b'\x00' * 8:
                    break # Reached empty memory
                confidence, concept_id = struct.unpack('fI', block)
                results.append({"confidence": confidence, "concept_id": concept_id})
            mm.close()
        return results

zero_copy_substrate = ZeroCopyMemorySubstrate()
