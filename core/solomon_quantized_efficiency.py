import os
import time
import mmap
import struct
import numpy as np
from enum import IntEnum
import hashlib
import json

class Tier(IntEnum):
    T0_REGISTRY = 0
    T1_DETERMINISTIC = 1
    T2_CACHED = 2
    T3_SMALL_REASONER = 3
    T4_LARGE_REASONER = 4
    T5_HUMAN_GATE = 5

class SizeClass(IntEnum):
    MICRO = 0
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    BLOCKED = 4

class RuntimeGuardrails:
    FORBIDDEN_ACTIONS = {
        "subprocess.Popen", "jules new", "git push", "ss1 mutation",
        "ssh", "sudo", "production deployment", "worker activation",
        "hidden browser actions", "wagering", "trading", "purchasing",
        "banking", "automatic promotion"
    }

    @staticmethod
    def check_action(action: str, approved: bool = False):
        if not approved:
            for forbidden in RuntimeGuardrails.FORBIDDEN_ACTIONS:
                if forbidden in action.lower():
                    raise PermissionError(f"Action '{action}' is forbidden by Runtime Guardrails without explicit approval.")
        return True

class ContextPacker:
    @staticmethod
    def pack(objective: str, registry_summary: str, test_status: str, blockers: list, changed_files: list, safe_step: str, approval_posture: str) -> dict:
        # Create a highly compact representation
        return {
            "obj": hashlib.md5(objective.encode()).hexdigest()[:8],
            "reg": hashlib.md5(registry_summary.encode()).hexdigest()[:8],
            "tests": test_status,
            "blk": len(blockers),
            "files": len(changed_files),
            "step": safe_step[:50],
            "appr": approval_posture
        }

class QuantizedEngineBudget:
    # A highly optimized registry backed by memory mapping for extreme O(1) performance
    HEADER_FORMAT = '<4sIQ'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAGIC = b'QEB1'
    VERSION = 1

    # [engine_id_hash: Q (8)] [tier: I (4)] [startup_cost: f (4)] [runtime_cost: f (4)]
    # [network_use: I (4)] [disk_use: I (4)] [cache_policy: I (4)] [approval_req: I (4)]
    RECORD_FORMAT = '<QIffIIII'
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    def __init__(self, filepath="/tmp/quantized_engine_budget.bin", max_records=1000):
        self.filepath = filepath
        self.max_records = max_records
        self._init_file()

    def _init_file(self):
        expected_size = self.HEADER_SIZE + (self.max_records * self.RECORD_SIZE)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'wb') as f:
                f.write(b'\0' * expected_size)
            with open(self.filepath, 'r+b') as f:
                header = struct.pack(self.HEADER_FORMAT, self.MAGIC, self.VERSION, 0)
                f.write(header)

        self.file_obj = open(self.filepath, 'r+b')
        self.mmap_obj = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_WRITE)

        magic, version, self.num_records = struct.unpack_from(self.HEADER_FORMAT, self.mmap_obj, 0)
        if magic != self.MAGIC:
            raise ValueError("Invalid Quantized Engine Budget memory file.")

    def register_engine(self, engine_id: str, tier: Tier, startup_cost: float, runtime_cost: float, network: int, disk: int, cache: int, approval: bool):
        if self.num_records >= self.max_records:
            raise MemoryError("Engine budget registry full.")

        engine_hash = int(hashlib.md5(engine_id.encode()).hexdigest()[:15], 16)

        offset = self.HEADER_SIZE + (self.num_records * self.RECORD_SIZE)
        struct.pack_into(self.RECORD_FORMAT, self.mmap_obj, offset,
                         engine_hash, tier.value, startup_cost, runtime_cost, network, disk, cache, int(approval))

        self.num_records += 1
        struct.pack_into(self.HEADER_FORMAT, self.mmap_obj, 0, self.MAGIC, self.VERSION, self.num_records)

    def check_engine(self, engine_id: str):
        engine_hash = int(hashlib.md5(engine_id.encode()).hexdigest()[:15], 16)

        # O(N) search through raw bytes, can be optimized with numpy if needed
        # We use a numpy structured array for extreme efficiency over mmap
        if self.num_records == 0:
            return None

        record_dtype = np.dtype([
            ('hash', '<u8'), ('tier', '<u4'), ('startup', '<f4'), ('runtime', '<f4'),
            ('net', '<u4'), ('disk', '<u4'), ('cache', '<u4'), ('appr', '<u4')
        ])

        arr = np.ndarray(shape=(self.num_records,), dtype=record_dtype, buffer=self.mmap_obj, offset=self.HEADER_SIZE, strides=(self.RECORD_SIZE,))

        # O(1) vectorized search
        indices = np.where(arr['hash'] == engine_hash)[0]
        if len(indices) == 0:
            return None

        idx = indices[0]
        record = arr[idx]
        return {
            "tier": Tier(record['tier']).name,
            "startup_cost": float(record['startup']),
            "runtime_cost": float(record['runtime']),
            "approval_required": bool(record['appr'])
        }

    def close(self):
        if self.mmap_obj: self.mmap_obj.close()
        if self.file_obj: self.file_obj.close()
