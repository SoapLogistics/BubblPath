import os
import time
import struct
import mmap
import threading
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Constants for mmap struct
# Header: Magic(4s), Version(I), MaxRecords(I), CurrentRecords(I)
HEADER_FMT = "4s I I I"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

# Record: ID(32s), State(32s), Task(64s), HeartbeatTS(d), CheckpointTS(d), CPU(d), MEM(d), Uptime(d), padding to 256 bytes
# 32+32+64+8+8+8+8+8 = 168 bytes + 88 bytes padding = 256 bytes
RECORD_FMT = "32s 32s 64s d d d d d 88x"
RECORD_SIZE = struct.calcsize(RECORD_FMT)

MAX_RESIDENTS = 32

class CheckpointEngine:
    """Zero-copy memory mapped checkpointing for residents."""
    def __init__(self, filename: str = "resident_checkpoints.bin"):
        self.filename = filename
        self.lock = threading.RLock()
        self.mmap_obj = None
        self.file_obj = None
        self._init_mmap()
        self.registry: Dict[str, int] = {} # resident_id -> index
        self._load_registry()

    def _init_mmap(self):
        file_size = HEADER_SIZE + (MAX_RESIDENTS * RECORD_SIZE)
        exists = os.path.exists(self.filename)

        self.file_obj = open(self.filename, "a+b" if exists else "w+b")
        if not exists or os.path.getsize(self.filename) < file_size:
            self.file_obj.truncate(file_size)
            self.file_obj.flush()

            self.mmap_obj = mmap.mmap(self.file_obj.fileno(), file_size, access=mmap.ACCESS_WRITE)
            struct.pack_into(HEADER_FMT, self.mmap_obj, 0, b"RSDN", 1, MAX_RESIDENTS, 0)
        else:
            self.mmap_obj = mmap.mmap(self.file_obj.fileno(), file_size, access=mmap.ACCESS_WRITE)

    def _load_registry(self):
        magic, version, max_rec, cur_rec = struct.unpack_from(HEADER_FMT, self.mmap_obj, 0)
        for i in range(cur_rec):
            offset = HEADER_SIZE + (i * RECORD_SIZE)
            data = struct.unpack_from(RECORD_FMT, self.mmap_obj, offset)
            rid = data[0].rstrip(b'\x00').decode('utf-8', errors='ignore')
            if rid:
                self.registry[rid] = i

    def _get_or_create_index(self, resident_id: str) -> int:
        with self.lock:
            if resident_id in self.registry:
                return self.registry[resident_id]

            magic, version, max_rec, cur_rec = struct.unpack_from(HEADER_FMT, self.mmap_obj, 0)
            if cur_rec >= max_rec:
                raise RuntimeError("Max residents reached in CheckpointEngine")

            idx = cur_rec
            self.registry[resident_id] = idx
            struct.pack_into(HEADER_FMT, self.mmap_obj, 0, magic, version, max_rec, cur_rec + 1)
            return idx

    def write_checkpoint(self, resident_id: str, state: str, task: str,
                         heartbeat_ts: float, checkpoint_ts: float, cpu: float, mem: float, uptime: float):
        idx = self._get_or_create_index(resident_id)
        offset = HEADER_SIZE + (idx * RECORD_SIZE)

        rid_b = resident_id.encode('utf-8')[:32].ljust(32, b'\x00')
        state_b = state.encode('utf-8')[:32].ljust(32, b'\x00')
        task_b = task.encode('utf-8')[:64].ljust(64, b'\x00')

        with self.lock:
            struct.pack_into(RECORD_FMT, self.mmap_obj, offset,
                             rid_b, state_b, task_b, heartbeat_ts, checkpoint_ts, cpu, mem, uptime)

    def read_checkpoint(self, resident_id: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            if resident_id not in self.registry:
                return None
            idx = self.registry[resident_id]
            offset = HEADER_SIZE + (idx * RECORD_SIZE)
            data = struct.unpack_from(RECORD_FMT, self.mmap_obj, offset)

            return {
                "id": data[0].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "state": data[1].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "task": data[2].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "heartbeat_ts": data[3],
                "checkpoint_ts": data[4],
                "cpu": data[5],
                "mem": data[6],
                "uptime": data[7]
            }

    def read_all(self) -> List[Dict[str, Any]]:
        with self.lock:
            results = []
            magic, version, max_rec, cur_rec = struct.unpack_from(HEADER_FMT, self.mmap_obj, 0)
            for i in range(cur_rec):
                offset = HEADER_SIZE + (i * RECORD_SIZE)
                data = struct.unpack_from(RECORD_FMT, self.mmap_obj, offset)
                rid = data[0].rstrip(b'\x00').decode('utf-8', errors='ignore')
                if rid:
                    results.append({
                        "id": rid,
                        "state": data[1].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                        "task": data[2].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                        "heartbeat_ts": data[3],
                        "checkpoint_ts": data[4],
                        "cpu": data[5],
                        "mem": data[6],
                        "uptime": data[7]
                    })
            return results

class ResidentMessaging:
    def __init__(self):
        self.lock = threading.RLock()
        self.messages: List[Dict[str, Any]] = []

    def publish(self, sender: str, msg_type: str, payload: Dict[str, Any]):
        with self.lock:
            self.messages.append({
                "ts": time.time(),
                "sender": sender,
                "type": msg_type,
                "payload": payload
            })
            # Keep bounded
            if len(self.messages) > 1000:
                self.messages = self.messages[-500:]

    def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self.lock:
            return self.messages[-limit:]

global_messaging = ResidentMessaging()
global_checkpointer = CheckpointEngine()

class Resident(ABC):
    """Base class for all permanent caretakers."""
    def __init__(self, resident_id: str):
        self.resident_id = resident_id
        self.state = "INIT"
        self.task = "Waking"
        self.start_time = time.time()
        self.last_checkpoint = self.start_time
        self.last_heartbeat = self.start_time
        self._running = False
        self._thread = None

    def _publish_heartbeat(self):
        self.last_heartbeat = time.time()
        # Mock resource usage
        cpu = 0.1
        mem = 10.0
        uptime = time.time() - self.start_time
        global_checkpointer.write_checkpoint(
            self.resident_id, self.state, self.task,
            self.last_heartbeat, self.last_checkpoint,
            cpu, mem, uptime
        )

    def _publish_checkpoint(self):
        self.last_checkpoint = time.time()
        self._publish_heartbeat()

    def publish_event(self, event_type: str, payload: dict):
        global_messaging.publish(self.resident_id, event_type, payload)

    def start(self):
        if self._running:
            return
        self._running = True
        self.state = "RUNNING"
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name=f"Resident-{self.resident_id}")
        self._thread.start()

    def stop(self):
        self._running = False
        self.state = "STOPPED"
        self.task = "Sleeping"
        self._publish_checkpoint()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run_loop(self):
        self.recover_state()
        while self._running:
            try:
                self._publish_heartbeat()
                self.cycle()
                self._publish_checkpoint()
                # Sleep until next cycle
                time.sleep(5.0)
            except Exception as e:
                logger.error(f"Resident {self.resident_id} error in loop: {e}")
                self.state = "ERROR"
                self.task = str(e)[:64]
                self._publish_checkpoint()
                time.sleep(10.0) # Backoff
                self.state = "RUNNING"

    @abstractmethod
    def recover_state(self):
        pass

    @abstractmethod
    def cycle(self):
        pass

class LifecycleEngine:
    def __init__(self):
        self.residents: Dict[str, Resident] = {}
        self.lock = threading.RLock()

    def register(self, resident: Resident):
        with self.lock:
            self.residents[resident.resident_id] = resident

    def start_all(self):
        with self.lock:
            for r in self.residents.values():
                r.start()

    def stop_all(self):
        with self.lock:
            for r in self.residents.values():
                r.stop()

global_lifecycle = LifecycleEngine()
