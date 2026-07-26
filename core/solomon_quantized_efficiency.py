import os
import time
import struct
import mmap
from enum import Enum

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class Tier(Enum):
    T1_deterministic_for_dry_run = 1
    T2_low_risk_auto_approved = 2
    T3_governance_reviewed = 3
    T4_human_in_the_loop = 4
    T5_human_gate = 5

class SizeClass(Enum):
    NANO = 1
    MICRO = 2
    SMALL = 3
    MEDIUM = 4
    LARGE = 5
    OMEGA = 6

class RuntimeGuardrails:
    def __init__(self, max_memory_mb=256, max_cpu_time_s=10.0, require_approval_above_tier=Tier.T2_low_risk_auto_approved):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time_s = max_cpu_time_s
        self.require_approval_above_tier = require_approval_above_tier

class QuantizedEngineBudget:
    def __init__(self, budget_file="solomon_budget.bin", max_entries=1000):
        self.budget_file = budget_file
        self.max_entries = max_entries
        self.entry_size = 24  # 8 bytes ID + 8 bytes (double) CPU + 8 bytes (double) MEM

        if not os.path.exists(self.budget_file):
            with open(self.budget_file, "wb") as f:
                f.write(b'\x00' * (self.entry_size * self.max_entries))

        self.f = open(self.budget_file, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), 0)

    def update_usage(self, entry_index, cpu_s, mem_mb):
        if entry_index < 0 or entry_index >= self.max_entries:
            raise ValueError("Index out of bounds")

        offset = entry_index * self.entry_size
        self.mm.seek(offset)

        # Read existing
        current_data = self.mm.read(self.entry_size)
        if len(current_data) == self.entry_size:
            current_id, current_cpu, current_mem = struct.unpack("!Qdd", current_data)

            # Update (simple increment for now)
            new_cpu = current_cpu + cpu_s
            new_mem = max(current_mem, mem_mb) # Keep high water mark

            self.mm.seek(offset)
            self.mm.write(struct.pack("!Qdd", current_id, new_cpu, new_mem))
            self.mm.flush()

    def get_usage(self, entry_index):
        if entry_index < 0 or entry_index >= self.max_entries:
            raise ValueError("Index out of bounds")

        offset = entry_index * self.entry_size
        self.mm.seek(offset)
        data = self.mm.read(self.entry_size)
        if len(data) == self.entry_size:
            _, cpu, mem = struct.unpack("!Qdd", data)
            return cpu, mem
        return 0.0, 0.0

    def close(self):
        self.mm.close()
        self.f.close()
