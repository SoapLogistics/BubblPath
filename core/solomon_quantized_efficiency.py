import mmap
import struct
from enum import Enum
import time

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class Tier(Enum):
    T1_deterministic_for_dry_run = 1
    T2_stateless_service = 2
    T3_stateful_read = 3
    T4_stateful_write = 4
    T5_human_gate = 5

class SizeClass(Enum):
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"

class RuntimeGuardrails:
    __slots__ = ['max_memory_mb', 'max_cpu_time_sec', 'allowed_network', 'allowed_fs']

    def __init__(self, max_memory_mb=128, max_cpu_time_sec=10.0, allowed_network=False, allowed_fs=False):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time_sec = max_cpu_time_sec
        self.allowed_network = allowed_network
        self.allowed_fs = allowed_fs

class QuantizedEngineBudget:
    """
    O(1) memory-mapped budget tracker using numpy and mmap for extreme efficiency.
    Gracefully falls back if numpy is missing.
    """
    __slots__ = ['filename', 'f', 'mm', 'array', 'max_entries', 'entry_size']

    def __init__(self, filename="quantized_budget.bin", max_entries=1000):
        self.filename = filename
        self.max_entries = max_entries

        # 16 bytes per entry:
        # - engine_id hash (uint32)
        # - tier (uint8)
        # - padding (3 bytes)
        # - memory_used_mb (float32)
        # - cpu_time_ms (float32)
        self.entry_size = 16
        file_size = self.entry_size * max_entries

        import os
        if not os.path.exists(self.filename):
            with open(self.filename, "wb") as f:
                f.write(b'\x00' * file_size)

        self.f = open(self.filename, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), file_size, access=mmap.ACCESS_WRITE)

        if HAS_NUMPY:
            self.array = np.ndarray(buffer=self.mm, dtype=[
                ('engine_id_hash', 'u4'),
                ('tier', 'u1'),
                ('pad', 'V3'),
                ('mem_mb', 'f4'),
                ('cpu_ms', 'f4')
            ], shape=(max_entries,))
        else:
            self.array = None

    def close(self):
        if self.mm:
            self.mm.close()
        if self.f:
            self.f.close()

    def record_usage(self, engine_id: str, tier: Tier, mem_mb: float, cpu_ms: float):
        engine_hash = hash(engine_id) & 0xffffffff
        slot = engine_hash % self.max_entries

        if HAS_NUMPY:
            self.array[slot]['engine_id_hash'] = engine_hash
            self.array[slot]['tier'] = tier.value
            self.array[slot]['mem_mb'] = mem_mb
            self.array[slot]['cpu_ms'] = cpu_ms
        else:
            offset = slot * self.entry_size
            struct.pack_into('<IB3xff', self.mm, offset, engine_hash, tier.value, mem_mb, cpu_ms)

def measure_efficiency(func):
    """Decorator to measure and record optimization metrics"""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return result, duration
    return wrapper
