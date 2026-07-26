import os
import mmap
import struct
import time
import threading
from abc import ABC, abstractmethod

# Resident State Format
# 64 bytes total:
# - 32 bytes name (string)
# - 8 bytes last_heartbeat (double)
# - 4 bytes state_code (uint32)
# - 4 bytes task_id (uint32)
# - 8 bytes last_checkpoint (double)
# - 4 bytes reserved
# - 4 bytes reserved
RESIDENT_STRUCT_FMT = '32s d I I d I I'
RESIDENT_STRUCT_SIZE = struct.calcsize(RESIDENT_STRUCT_FMT)

MAX_RESIDENTS = 16
SHM_FILE = 'solomon_residents.bin'

class ResidentState:
    __slots__ = ['name', 'last_heartbeat', 'state_code', 'task_id', 'last_checkpoint']
    def __init__(self, name: str, last_heartbeat: float, state_code: int, task_id: int, last_checkpoint: float):
        self.name = name
        self.last_heartbeat = last_heartbeat
        self.state_code = state_code
        self.task_id = task_id
        self.last_checkpoint = last_checkpoint

class ResidentFramework:
    """
    Zero-copy memory-mapped lifecycle engine for Residents.
    Provides registration, watchdog, checkpointing, and heartbeat monitoring.
    """
    def __init__(self, file_path=SHM_FILE):
        self.file_path = file_path
        self._ensure_file()
        self.f = open(self.file_path, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), MAX_RESIDENTS * RESIDENT_STRUCT_SIZE)
        self.lock = threading.RLock()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "wb") as f:
                f.write(b'\x00' * (MAX_RESIDENTS * RESIDENT_STRUCT_SIZE))

    def _get_index(self, name: str) -> int:
        encoded_name = name.encode('utf-8')[:32].ljust(32, b'\x00')
        with self.lock:
            for i in range(MAX_RESIDENTS):
                offset = i * RESIDENT_STRUCT_SIZE
                data = self.mm[offset:offset+RESIDENT_STRUCT_SIZE]
                if data.startswith(encoded_name):
                    return i
            # Not found, find empty slot
            for i in range(MAX_RESIDENTS):
                offset = i * RESIDENT_STRUCT_SIZE
                data = self.mm[offset:offset+RESIDENT_STRUCT_SIZE]
                if data.startswith(b'\x00' * 32):
                    self.mm[offset:offset+32] = encoded_name
                    return i
        raise RuntimeError("No available slots for new Resident.")

    def update_heartbeat(self, name: str, state_code: int, task_id: int):
        idx = self._get_index(name)
        offset = idx * RESIDENT_STRUCT_SIZE
        now = time.time()
        with self.lock:
            data = self.mm[offset:offset+RESIDENT_STRUCT_SIZE]
            unpacked = list(struct.unpack(RESIDENT_STRUCT_FMT, data))
            encoded_name = name.encode('utf-8')[:32].ljust(32, b'\x00')
            packed = struct.pack(RESIDENT_STRUCT_FMT, encoded_name, now, state_code, task_id, unpacked[4], 0, 0)
            self.mm[offset:offset+RESIDENT_STRUCT_SIZE] = packed

    def update_checkpoint(self, name: str):
        idx = self._get_index(name)
        offset = idx * RESIDENT_STRUCT_SIZE
        now = time.time()
        with self.lock:
            data = self.mm[offset:offset+RESIDENT_STRUCT_SIZE]
            unpacked = list(struct.unpack(RESIDENT_STRUCT_FMT, data))
            encoded_name = name.encode('utf-8')[:32].ljust(32, b'\x00')
            packed = struct.pack(RESIDENT_STRUCT_FMT, encoded_name, unpacked[1], unpacked[2], unpacked[3], now, 0, 0)
            self.mm[offset:offset+RESIDENT_STRUCT_SIZE] = packed

    def get_resident_state(self, name: str) -> ResidentState:
        idx = self._get_index(name)
        offset = idx * RESIDENT_STRUCT_SIZE
        with self.lock:
            data = self.mm[offset:offset+RESIDENT_STRUCT_SIZE]
        unpacked = struct.unpack(RESIDENT_STRUCT_FMT, data)
        return ResidentState(
            name=unpacked[0].rstrip(b'\x00').decode('utf-8', errors='ignore'),
            last_heartbeat=unpacked[1],
            state_code=unpacked[2],
            task_id=unpacked[3],
            last_checkpoint=unpacked[4]
        )

    def get_all_states(self):
        states = []
        with self.lock:
            for i in range(MAX_RESIDENTS):
                offset = i * RESIDENT_STRUCT_SIZE
                data = self.mm[offset:offset+RESIDENT_STRUCT_SIZE]
                if not data.startswith(b'\x00' * 32):
                    unpacked = struct.unpack(RESIDENT_STRUCT_FMT, data)
                    states.append(ResidentState(
                        name=unpacked[0].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                        last_heartbeat=unpacked[1],
                        state_code=unpacked[2],
                        task_id=unpacked[3],
                        last_checkpoint=unpacked[4]
                    ))
        return states

    def shutdown(self):
        self.mm.flush()
        self.mm.close()
        self.f.close()

class Resident(ABC):
    """
    Abstract Base Class for permanent Solomon caretakers (Guardian, Jules).
    Enforces the 9-step runtime loop.
    """
    def __init__(self, name: str, framework: ResidentFramework):
        self.name = name
        self.framework = framework
        self._stop_event = threading.Event()
        self.current_state_code = 0
        self.current_task_id = 0

    def start(self):
        self.thread = threading.Thread(target=self._run_loop, name=f"Resident_{self.name}", daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        if hasattr(self, 'thread'):
            self.thread.join()

    def _run_loop(self):
        # Step 1: Wake
        self.wake()

        # Step 2: Recover state
        self.recover_state()

        while not self._stop_event.is_set():
            # Step 3: Publish heartbeat
            self.framework.update_heartbeat(self.name, self.current_state_code, self.current_task_id)

            # Step 4: Scan assigned domain
            scan_results = self.scan_assigned_domain()

            # Step 5: Collect evidence
            evidence = self.collect_evidence(scan_results)

            # Step 6: Produce findings
            findings = self.produce_findings(evidence)

            # Step 7: Prepare governed proposals if needed
            if findings:
                self.prepare_governed_proposals(findings)

            # Step 8: Checkpoint
            self.checkpoint()

            # Step 9: Sleep until next cycle or event
            self._stop_event.wait(self.sleep_interval())

    @abstractmethod
    def wake(self): pass

    @abstractmethod
    def recover_state(self): pass

    @abstractmethod
    def scan_assigned_domain(self): pass

    @abstractmethod
    def collect_evidence(self, scan_results): pass

    @abstractmethod
    def produce_findings(self, evidence): pass

    @abstractmethod
    def prepare_governed_proposals(self, findings): pass

    @abstractmethod
    def checkpoint(self): pass

    @abstractmethod
    def sleep_interval(self) -> float: pass
