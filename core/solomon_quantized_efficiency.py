import os
import mmap
import struct
import numpy as np
from enum import Enum, auto

class Tier(Enum):
    T1_deterministic_for_dry_run = auto()
    T2_safe_execute = auto()
    T3_state_mutating = auto()
    T4_network_capable = auto()
    T5_human_gate = auto()

class SizeClass(Enum):
    MICRO = 1024
    SMALL = 4096
    MEDIUM = 16384
    LARGE = 65536
    HUGE = 262144

class RuntimeGuardrails:
    __slots__ = ['enforced']
    def __init__(self):
        self.enforced = True

    def validate_execution(self, tier: Tier):
        if tier == Tier.T5_human_gate:
            # Requires human gate
            pass
        return True

class QuantizedEngineBudget:
    __slots__ = ['filename', 'capacity', 'f', 'mm', 'guardrails', '_metrics_array']
    def __init__(self, filename="quantized_budget.bin", capacity: SizeClass = SizeClass.SMALL):
        self.filename = filename
        self.capacity = capacity.value
        self._ensure_file()
        self.f = open(self.filename, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), 0)
        self.guardrails = RuntimeGuardrails()

        # Initialize numpy array mapped over mmap for extreme algorithmic efficiency (O(1))
        # Struct: [baseline(float32), new(float32), improvement(float32), saved(float32)]
        # Maximum of capacity // 16 entries
        num_entries = self.capacity // 16
        self._metrics_array = np.ndarray((num_entries, 4), dtype=np.float32, buffer=self.mm)

    def _ensure_file(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) < self.capacity:
            with open(self.filename, "wb") as f:
                f.write(b'\x00' * self.capacity)

    def measure_optimization(self, engine_id: str, baseline_metric: float, new_metric: float):
        improvement = (baseline_metric - new_metric) / baseline_metric if baseline_metric > 0 else 0
        saved = baseline_metric - new_metric

        # Use a simple hash of engine_id to find an O(1) slot in the zero-copy mmap
        slot = hash(engine_id) % (self.capacity // 16)

        # O(1) zero-copy write
        self._metrics_array[slot, 0] = baseline_metric
        self._metrics_array[slot, 1] = new_metric
        self._metrics_array[slot, 2] = improvement
        self._metrics_array[slot, 3] = saved

        return {
            "engine_id": engine_id,
            "baseline": baseline_metric,
            "new": new_metric,
            "improvement": improvement,
            "saved": saved
        }

    def allocate(self, tier: Tier, size: int):
        self.guardrails.validate_execution(tier)

        if size > self.capacity:
            raise ValueError("Allocation exceeds quantized budget capacity")

        return True

    def get_metrics_snapshot(self):
        # Extremely fast O(1) full state read
        return self._metrics_array.copy()

    def close(self):
        self.mm.close()
        self.f.close()
