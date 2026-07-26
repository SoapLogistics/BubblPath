import struct
import mmap
import os
import time
import hashlib
from typing import Dict, Any, List

# Optional numpy for fast aggregations
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class ObservabilityEngine:
    """
    MD9 Extreme Efficiency Observability Engine.
    Implements a lock-free (or minimal-lock), zero-copy memory mapped ring buffer
    for telemetry, health, and logs. Includes a header block for multi-process safety.
    """
    __slots__ = ['max_records', 'file_path', 'file_size', 'fd', 'mmap_obj']

    # Header: HeadPointer(Q) - 8 bytes
    HEADER_FORMAT = 'Q'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    # Timestamp(8), Component(1), Event(1), Severity(1), Duration(8), Result(1), CorrelationHash(16), ContextHash(16)
    # 8 + 1 + 1 + 1 + 8 + 1 + 16 + 16 = 52 bytes per record.
    RECORD_FORMAT = 'd B B B d B 16s 16s'
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    COMPONENTS = {
        "unknown": 0, "mnemosyne": 1, "prometheus": 2, "gabriel": 3,
        "runtime": 4, "registry": 5, "browser": 6, "governance": 7,
        "api": 8
    }

    SEVERITY = {
        "debug": 0, "info": 1, "warn": 2, "error": 3, "critical": 4
    }

    def __init__(self, max_records=100000, file_path="solomon_telemetry.bin"):
        self.max_records = max_records
        self.file_path = file_path
        self.file_size = self.HEADER_SIZE + (self.RECORD_SIZE * self.max_records)

        # Ensure file exists and is of correct size
        if not os.path.exists(self.file_path):
            with open(self.file_path, "wb") as f:
                # Pre-allocate large file quickly
                f.write(b'\x00' * self.file_size)
        else:
            current_size = os.path.getsize(self.file_path)
            if current_size < self.file_size:
                with open(self.file_path, "ab") as f:
                    f.write(b'\x00' * (self.file_size - current_size))

        self.fd = os.open(self.file_path, os.O_RDWR)
        self.mmap_obj = mmap.mmap(self.fd, self.file_size, access=mmap.ACCESS_WRITE)

        # We don't find_head in a loop anymore, we read from the header.
        # But we do want to initialize the header if the file is completely fresh.
        head_val = struct.unpack_from(self.HEADER_FORMAT, self.mmap_obj, 0)[0]
        if head_val > self.max_records:
             # Safety fallback in case of corruption
            struct.pack_into(self.HEADER_FORMAT, self.mmap_obj, 0, 0)

    @property
    def head(self) -> int:
        return struct.unpack_from(self.HEADER_FORMAT, self.mmap_obj, 0)[0]

    @head.setter
    def head(self, val: int):
        struct.pack_into(self.HEADER_FORMAT, self.mmap_obj, 0, val)

    def record_event(self, component: str, event_type: int, severity: str, duration_ms: float, success: bool, corr_id: str, context: str):
        """Zero-IO blocking mmap write."""
        timestamp = time.time()
        c_id = self.COMPONENTS.get(component.lower(), 0)
        s_id = self.SEVERITY.get(severity.lower(), 1)
        res_id = 1 if success else 0

        corr_hash = hashlib.md5(corr_id.encode('utf-8')).digest()
        ctx_hash = hashlib.md5(context.encode('utf-8')).digest()

        record = struct.pack(
            self.RECORD_FORMAT,
            timestamp, c_id, event_type, s_id, duration_ms, res_id, corr_hash, ctx_hash
        )

        # Pseudo-atomic read/update cycle for multiprocessing
        current_head = self.head
        next_head = (current_head + 1) % self.max_records
        offset = self.HEADER_SIZE + (current_head * self.RECORD_SIZE)

        self.mmap_obj[offset:offset + self.RECORD_SIZE] = record
        self.head = next_head

    def get_recent_metrics(self, limit=100) -> List[Dict[str, Any]]:
        records = []
        # Calculate start safely for ring buffer
        current_head = self.head
        start = (current_head - limit) % self.max_records

        for i in range(limit):
            idx = (start + i) % self.max_records
            offset = self.HEADER_SIZE + (idx * self.RECORD_SIZE)
            raw = self.mmap_obj[offset:offset + self.RECORD_SIZE]
            ts, c_id, e_type, s_id, dur, res, chash, ctxhash = struct.unpack(self.RECORD_FORMAT, raw)

            if ts == 0.0:
                continue # Skip empty

            records.append({
                "timestamp": ts,
                "component_id": c_id,
                "event_type": e_type,
                "severity_id": s_id,
                "duration_ms": dur,
                "success": bool(res),
                "correlation_hash": chash.hex(),
                "context_hash": ctxhash.hex()
            })
        return records

    def close(self):
        self.mmap_obj.close()
        os.close(self.fd)

# Global singleton
telemetry = ObservabilityEngine()
