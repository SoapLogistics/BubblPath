import hashlib
import mmap
import os
import struct
import time
from typing import Any


class SolomonMetricsEngine:
    """
    Ultra-efficient binary metrics engine using memory-mapped I/O.
    Enforces that every interaction is recorded as an experiment.
    Format: timestamp(d), duration(d), success(?), valence(f), arousal(f), endpoint(32s), req_hash(16s)
    """
    RECORD_FORMAT = 'dd?ff32s16s'
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    def __init__(self, max_records=100000, file_path="solomon_metrics.bin"):
        self.max_records = max_records
        self.file_path = file_path
        self.file_size = self.RECORD_SIZE * self.max_records

        # Ensure file exists and is of correct size
        if not os.path.exists(self.file_path):
            with open(self.file_path, "wb") as f:
                f.write(b'\x00' * self.file_size)
        else:
            # Resize if existing file is smaller
            current_size = os.path.getsize(self.file_path)
            if current_size < self.file_size:
                with open(self.file_path, "ab") as f:
                    f.write(b'\x00' * (self.file_size - current_size))

        self.fd = os.open(self.file_path, os.O_RDWR)
        self.mmap_obj = mmap.mmap(self.fd, self.file_size, access=mmap.ACCESS_WRITE)
        self.head = self._find_head()

    def _find_head(self) -> int:
        """Find the next empty slot using binary search/linear fallback."""
        for i in range(self.max_records):
            offset = i * self.RECORD_SIZE
            ts = struct.unpack_from('d', self.mmap_obj, offset)[0]
            if ts == 0.0:
                return i
        return 0 # Wrap around if full (ring buffer)

    def record_interaction(self, duration_ms: float, success: bool, valence: float, arousal: float, endpoint: str, request_content: str):
        """Records an interaction with zero-IO blocking overhead via mmap."""
        timestamp = time.time()

        # Truncate and encode strings (increased to 32 bytes)
        endpoint_b = endpoint[:32].encode('utf-8').ljust(32, b'\x00')

        # Create a deterministic 16-byte hash of the request content
        req_hash = hashlib.md5(request_content.encode('utf-8')).digest()

        record = struct.pack(
            self.RECORD_FORMAT,
            timestamp,
            duration_ms,
            success,
            valence,
            arousal,
            endpoint_b,
            req_hash
        )

        offset = self.head * self.RECORD_SIZE
        self.mmap_obj[offset:offset + self.RECORD_SIZE] = record

        self.head = (self.head + 1) % self.max_records

    def get_all_records(self) -> list[dict[str, Any]]:
        """Reads all valid records from the mmap."""
        records = []
        for i in range(self.max_records):
            offset = i * self.RECORD_SIZE
            raw = self.mmap_obj[offset:offset + self.RECORD_SIZE]

            # Unpack
            ts, dur, success, val, aro, ep, rhash = struct.unpack(self.RECORD_FORMAT, raw)
            if ts == 0.0:
                break # Reached the end of populated data

            records.append({
                "timestamp": ts,
                "duration_ms": dur,
                "success": success,
                "valence": val,
                "arousal": aro,
                "endpoint": ep.decode('utf-8').rstrip('\x00'),
                "request_hash": rhash.hex()
            })
        return records

    def close(self):
        self.mmap_obj.close()
        os.close(self.fd)
