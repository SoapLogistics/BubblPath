import mmap
import struct
import os
import time

# Registry compliance
readiness_key = "solomon_validation_framework_active"

class ValidationEvidence:
    """
    Hyper-efficient memory structure for validation evidence using __slots__.
    """
    __slots__ = ["test_id", "status", "execution_time_ms", "memory_used_kb", "timestamp"]

    def __init__(self, test_id: int, status: int, execution_time_ms: float, memory_used_kb: float, timestamp: float):
        self.test_id = test_id
        self.status = status # 0 = fail, 1 = pass
        self.execution_time_ms = execution_time_ms
        self.memory_used_kb = memory_used_kb
        self.timestamp = timestamp


class ValidationFramework:
    """
    O(1) Zero-copy memory-mapped Validation Framework for Perpetual Learning.
    Records test evidence directly to a binary ring buffer to avoid memory degradation.
    """
    def __init__(self, log_path="validation_evidence.bin", max_entries=10000):
        self.log_path = log_path
        self.max_entries = max_entries
        self.entry_size = 32  # test_id(I), status(I), exec_time(d), mem_kb(d), ts(d) => 4+4+8+8+8 = 32 bytes
        # Add 4 bytes header to store the ring buffer current write index
        self.header_size = 4
        self.file_size = self.header_size + (self.entry_size * self.max_entries)
        self.struct_format = 'IIddd'
        self.header_format = 'I'

        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, "wb") as f:
                f.write(b'\x00' * self.file_size)

    def record_evidence(self, evidence: ValidationEvidence):
        """
        Records evidence in strict O(1) time using mmap, wrapping around as a true ring buffer.
        """
        try:
            with open(self.log_path, "r+b") as f:
                # Use zero-copy mapping
                mm = mmap.mmap(f.fileno(), 0)

                # O(1) Index retrieval
                current_idx = struct.unpack(self.header_format, mm[0:self.header_size])[0]

                # O(1) Offset computation
                offset = self.header_size + (current_idx * self.entry_size)

                packed_data = struct.pack(
                    self.struct_format,
                    evidence.test_id & 0xffffffff,  # safeguard integer size
                    evidence.status,
                    evidence.execution_time_ms,
                    evidence.memory_used_kb,
                    evidence.timestamp
                )
                mm[offset:offset + self.entry_size] = packed_data

                # O(1) Index increment and wrap-around (perpetual ring buffer logic)
                next_idx = (current_idx + 1) % self.max_entries
                mm[0:self.header_size] = struct.pack(self.header_format, next_idx)

                mm.flush()
                mm.close()
        except Exception as e:
            print(f"Error recording evidence: {e}")

    def read_all_evidence(self):
        """
        Reads all recorded evidence from the memory-mapped file.
        """
        results = []
        try:
            with open(self.log_path, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                for i in range(self.max_entries):
                    offset = self.header_size + (i * self.entry_size)
                    slot_data = mm[offset:offset + self.entry_size]
                    unpacked = struct.unpack(self.struct_format, slot_data)
                    # If timestamp > 0, it's a valid record
                    if unpacked[4] > 0.0:
                        results.append(ValidationEvidence(
                            test_id=unpacked[0],
                            status=unpacked[1],
                            execution_time_ms=unpacked[2],
                            memory_used_kb=unpacked[3],
                            timestamp=unpacked[4]
                        ))
                mm.close()
        except Exception as e:
            print(f"Error reading evidence: {e}")

        return results
