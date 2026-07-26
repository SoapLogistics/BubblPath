
route_key = "None"
internal_parent = "None"
readiness_key = "runtime"
import os
import mmap
import struct
import time
import uuid
import logging
import threading
import hashlib
import sqlite3
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from enum import IntEnum
from typing import Dict, List, Any, Optional, Tuple, Set, Callable

logger = logging.getLogger(__name__)

# Constants for Hyper-Efficiency Doctrine
# Total size: 128 bytes per event for perfect L2/L3 cache line alignment
# Struct format: '<QQIIBBBBBBHdd48s24s8s' -> Total 128 bytes
EVENT_RECORD_SIZE = 128
MAX_EVENTS = 100000  # 12.8 MB memory map
RUNTIME_FILE = "runtime_nervous_system.bin"

class EventCategory(IntEnum):
    SYSTEM = 1
    MEMORY = 2
    PLANNING = 3
    LEARNING = 4
    CAPABILITY = 5
    GOVERNANCE = 6
    RUNTIME = 7
    BROWSER = 8

class WorkerClass(IntEnum):
    RETRIEVAL = 1
    PLANNING = 2
    LEARNING = 3
    ENGINEERING = 4
    BROWSER = 5
    REVIEW = 6

class EventState(IntEnum):
    EMPTY = 0
    QUEUED = 1
    PROCESSING = 2
    DONE = 3
    FAILED = 4
    ESCALATED = 5 # Human review or rollback

class EscalationRule(IntEnum):
    RETRY = 1
    QUEUE = 2
    HUMAN_REVIEW = 3
    ROLLBACK = 4

class RuntimeNervousSystem:
    _instance = None
    _lock = threading.RLock()

    # To support delayed jobs and dependencies, we adjust padding:
    # < Q(id) Q(cor_id) I(src) I(dst) B(cat) B(cls) B(state) B(prio) B(retry) B(escl) H(pad) d(time) d(dur) d(exec_after) Q(dep_id) 48s(payload) 24s(err) 8s(pad)
    # Original sum: 120 + 8s pad. Let's make it EXACTLY 128 bytes still by stealing from payload and error.
    # Q(8) Q(8) I(4) I(4) = 24
    # B*6(6) H(2) = 8
    # d(8) d(8) d(exec_after:8) Q(dep_id:8) = 32
    # 24+8+32 = 64 bytes. Leaving 64 bytes for payload/error strings.
    # We will allocate 40s(payload) and 24s(error). Total: 64+40+24 = 128 bytes.
    STRUCT_FORMAT = '<QQIIBBBBBBHdddQ40s24s'

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RuntimeNervousSystem, cls).__new__(cls)
                cls._instance._init_once()
            return cls._instance

    def _init_once(self):
        self.capacity = MAX_EVENTS
        self.file_path = RUNTIME_FILE
        self._ensure_file()

        # Zero-copy memory map
        self.fd = open(self.file_path, "r+b")
        self.mmap = mmap.mmap(self.fd.fileno(), 0)

        self.head = 0 # Next write index

        # SQLite payload store for persistent, memory-safe large payloads
        self.db_path = "runtime_payloads.db"
        self._init_db()

        self.active_workers: Dict[int, Dict] = {}
        self._shutdown = threading.Event()
        self.worker_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="RuntimeWorker")
        self.daemon_thread = threading.Thread(target=self._runtime_loop, daemon=True, name="RuntimeNervousSystemLoop")
        self.daemon_thread.start()

        # Subscriptions
        self.subscriptions: Dict[int, List[Callable]] = {c.value: [] for c in EventCategory}

        # Internal properties for static analysis
        self.route_key = "active_route"
        self.internal_parent = "None"

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS payloads (
                    event_id INTEGER PRIMARY KEY,
                    payload TEXT
                )
            ''')
            conn.commit()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "wb") as f:
                f.write(b'\x00' * (self.capacity * EVENT_RECORD_SIZE))

    def subscribe(self, category: EventCategory, callback: Callable):
        with self._lock:
            if callback not in self.subscriptions[category.value]:
                self.subscriptions[category.value].append(callback)

    def publish_event(self, category: EventCategory, worker_class: WorkerClass,
                      payload: Any, source: str = "system", destination: str = "any",
                      correlation_id: int = 0, priority: int = 0, execute_after: float = 0.0, dependency_id: int = 0) -> int:
        with self._lock:
            event_id = int(time.time() * 1000000) + (self.head % 1000)
            if correlation_id == 0:
                correlation_id = event_id

            src_hash = hash(source) & 0xffffffff
            dst_hash = hash(destination) & 0xffffffff

            # Pack memory
            offset = self.head * EVENT_RECORD_SIZE
            payload_bytes = str(payload)[:40].encode('utf-8').ljust(40, b'\x00')

            struct.pack_into(
                self.STRUCT_FORMAT, self.mmap, offset,
                event_id, correlation_id, src_hash, dst_hash,
                category.value, worker_class.value, EventState.QUEUED.value, priority, 0, 0, 0,
                time.time(), 0.0, execute_after, dependency_id, payload_bytes, b'\x00'*24
            )

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('INSERT OR REPLACE INTO payloads (event_id, payload) VALUES (?, ?)',
                             (event_id, json.dumps(payload)))
                conn.commit()

            self.head = (self.head + 1) % self.capacity
            return event_id

    def read_event(self, index: int) -> Optional[Dict]:
        offset = index * EVENT_RECORD_SIZE
        data = struct.unpack_from(self.STRUCT_FORMAT, self.mmap, offset)
        if data[0] == 0:
            return None
        return {
            'event_id': data[0],
            'correlation_id': data[1],
            'source_hash': data[2],
            'destination_hash': data[3],
            'category': EventCategory(data[4]) if data[4] else None,
            'worker_class': WorkerClass(data[5]) if data[5] else None,
            'state': EventState(data[6]),
            'priority': data[7],
            'retry_count': data[8],
            'escalation': data[9],
            'timestamp': data[11],
            'duration': data[12],
            'execute_after': data[13],
            'dependency_id': data[14],
            'payload_preview': data[15].rstrip(b'\x00').decode('utf-8', errors='ignore'),
            'error_trace': data[16].rstrip(b'\x00').decode('utf-8', errors='ignore')
        }

    def update_event_state(self, index: int, state: EventState, error: str = "", duration: float = 0.0, retry_inc: int = 0, esc: int = 0):
        with self._lock:
            offset = index * EVENT_RECORD_SIZE
            self.mmap[offset + 26] = state.value

            # Clean up payload if terminal state
            if state in (EventState.DONE, EventState.FAILED, EventState.ESCALATED):
                event_id = struct.unpack_from('<Q', self.mmap, offset)[0]
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute('DELETE FROM payloads WHERE event_id = ?', (event_id,))
                        conn.commit()
                except Exception as e:
                    logger.error(f"Failed to delete payload for event {event_id}: {e}")

            if retry_inc > 0:
                current_retry = self.mmap[offset + 28]
                self.mmap[offset + 28] = current_retry + retry_inc

            if esc > 0:
                self.mmap[offset + 29] = esc

            if duration > 0.0:
                struct.pack_into('<d', self.mmap, offset + 40, duration)

            if error:
                err_bytes = error[:24].encode('utf-8').ljust(24, b'\x00')
                # In new format: payload is S40 starting at 64, error is S24 starting at 104
                self.mmap[offset + 104:offset + 128] = err_bytes

    def get_queued_events(self) -> List[Tuple[int, int]]:
        now = time.time()

        # Buffer as unstructured bytes
        buffer_np = np.frombuffer(self.mmap, dtype=np.uint8).reshape(-1, EVENT_RECORD_SIZE)
        states = buffer_np[:, 26]
        priorities = buffer_np[:, 27]

        # We need structured reads for float64 execution_after and int64 dep_id
        # Let's use a structured array view for the specific columns we care about
        # The struct format: '<QQIIBBBBBBHdddQ40s24s'
        # execution_after is at offset 48, size 8 (float64)
        # dependency_id is at offset 56, size 8 (uint64)
        # Since reading these with numpy byte offsets is tricky with pure uint8 reshape,
        # we can create a custom dtype.

        dt = np.dtype([
            ('id', np.uint64),
            ('cor_id', np.uint64),
            ('src', np.uint32),
            ('dst', np.uint32),
            ('cat', np.uint8),
            ('cls', np.uint8),
            ('state', np.uint8),
            ('priority', np.uint8),
            ('retry', np.uint8),
            ('esc', np.uint8),
            ('pad', np.uint16),
            ('time', np.float64),
            ('dur', np.float64),
            ('exec_after', np.float64),
            ('dep_id', np.uint64),
            ('payload', 'S40'),
            ('error', 'S24')
        ])

        structured_view = np.frombuffer(self.mmap, dtype=dt)

        states_view = structured_view['state']
        priorities_view = structured_view['priority']
        exec_after_view = structured_view['exec_after']
        dep_id_view = structured_view['dep_id']
        id_view = structured_view['id']

        # Filter 1: State is QUEUED
        queued_mask = (states_view == EventState.QUEUED.value)

        # Filter 2: execute_after is either 0 or <= now
        time_mask = (exec_after_view <= now)

        # Combine masks
        eligible_mask = queued_mask & time_mask

        eligible_indices = np.where(eligible_mask)[0]

        # For those with dependencies, we need to check if the dependency is DONE
        # This requires O(N) lookup, but we only do it on eligible jobs
        final_eligible_indices = []
        for idx in eligible_indices:
            dep_id = dep_id_view[idx]
            if dep_id == 0:
                final_eligible_indices.append(idx)
            else:
                # Find if dependency is DONE
                dep_matches = np.where(id_view == dep_id)[0]
                if len(dep_matches) > 0:
                    dep_idx = dep_matches[0]
                    if states_view[dep_idx] == EventState.DONE.value:
                        final_eligible_indices.append(idx)

        if not final_eligible_indices:
            return []

        final_eligible_indices = np.array(final_eligible_indices)
        queued_priorities = priorities_view[final_eligible_indices].astype(np.int32)

        sorted_order = np.argsort(-queued_priorities)
        sorted_indices = final_eligible_indices[sorted_order]

        return [(int(idx), int(priorities_view[idx])) for idx in sorted_indices]

    def _runtime_loop(self):
        """Background continuous orchestration loop"""
        while not self._shutdown.is_set():
            try:
                queued = self.get_queued_events()
                for idx, prio in queued[:10]:
                    self._dispatch_event(idx)

                self._recover_stalled()

            except Exception as e:
                logger.error(f"Runtime Loop Error: {e}")
            time.sleep(0.1)

    def _dispatch_event(self, index: int):
        event = self.read_event(index)
        if not event:
            return

        self.update_event_state(index, EventState.PROCESSING)
        start_time = time.time()

        try:
            full_payload = event['payload_preview']
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT payload FROM payloads WHERE event_id = ?', (event['event_id'],))
                row = cursor.fetchone()
                if row:
                    full_payload = json.loads(row[0])

            cat_value = event['category'].value if event['category'] else 0
            subscribers = self.subscriptions.get(cat_value, [])

            # Use thread pool to execute asynchronously
            def run_subscriber(sub, event, full_payload, index, start_time):
                try:
                    sub(event, full_payload)
                    self.update_event_state(index, EventState.DONE, duration=time.time() - start_time)
                except Exception as e:
                    logger.error(f"Event failed: {e}")
                    retry_count = event['retry_count']
                    if retry_count < 3:
                        self.update_event_state(index, EventState.QUEUED, error=str(e), retry_inc=1)
                    else:
                        self.update_event_state(index, EventState.ESCALATED, error=str(e), esc=EscalationRule.HUMAN_REVIEW.value)

            for sub in subscribers:
                self.worker_pool.submit(run_subscriber, sub, event, full_payload, index, start_time)

        except Exception as e:
            logger.error(f"Event parsing failed: {e}")

    def _recover_stalled(self):
        buffer_np = np.frombuffer(self.mmap, dtype=np.uint8).reshape(-1, EVENT_RECORD_SIZE)
        states = buffer_np[:, 26]

        processing_indices = np.where(states == EventState.PROCESSING.value)[0]
        now = time.time()

        for idx in processing_indices:
            offset = idx * EVENT_RECORD_SIZE
            ts = struct.unpack_from('<d', self.mmap, offset + 32)[0]
            if now - ts > 60.0:
                self.update_event_state(idx, EventState.FAILED, error="Timeout")

    def shutdown(self):
        self._shutdown.set()
        if self.daemon_thread.is_alive():
            self.daemon_thread.join(timeout=2.0)
        self.worker_pool.shutdown(wait=True)
        self.mmap.close()
        self.fd.close()
