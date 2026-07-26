import os
import mmap
import struct
import time
import uuid
import threading
import logging
from typing import Dict, List, Callable, Any, Optional

logger = logging.getLogger(__name__)

# Constants for Event Categories
class EventCategory:
    SYSTEM = 0x01
    MEMORY = 0x02
    PLANNING = 0x03
    LEARNING = 0x04
    CAPABILITY = 0x05
    GOVERNANCE = 0x06
    RUNTIME = 0x07
    BROWSER = 0x08

class EventStatus:
    PENDING = 0
    PROCESSING = 1
    SUCCESS = 2
    FAILED = 3

class ZeroCopyEventBus:
    """
    Zero-Copy Event Bus (O(1) memory-mapped circular buffer).
    Maximizes algorithmic efficiency by bypassing Python GC for event routing.
    """

    # Header format: [magic_bytes: 4s] [version: I] [head_ptr: Q] [tail_ptr: Q] [max_events: Q]
    # 4 + 4 + 8 + 8 + 8 = 32 bytes
    HEADER_FORMAT = '<4sIQQQ'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAGIC = b'NEUR'
    VERSION = 1

    # Event Record format (Cache-Line Aligned)
    # [id: 16s (UUID)] [category: B] [status: B] [priority: B] [retry_count: B]
    # [timestamp: Q] [source_hash: Q] [dest_hash: Q] [duration: I] [payload_hash: Q]
    # Total: 16 + 1 + 1 + 1 + 1 + 8 + 8 + 8 + 4 + 8 = 56 bytes. Pad to 64 bytes for L1 Cache alignment (8x).
    RECORD_FORMAT = '<16sBBBBQQQIQ8x'
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    def __init__(self, filepath: str = "nervous_system.bin", max_events: int = 10000):
        self.filepath = filepath
        self.max_events = max_events
        self.total_size = self.HEADER_SIZE + (self.max_events * self.RECORD_SIZE)
        self._lock = threading.RLock()
        self._subscribers: Dict[int, List[Callable]] = {}

        self._init_mmap()

    def _init_mmap(self):
        with self._lock:
            if not os.path.exists(self.filepath):
                with open(self.filepath, 'wb') as f:
                    f.write(b'\x00' * self.total_size)

            self.fd = open(self.filepath, 'r+b')
            self.mm = mmap.mmap(self.fd.fileno(), self.total_size, access=mmap.ACCESS_WRITE)

            # Read header
            header = self.mm[:self.HEADER_SIZE]
            magic, version, head_ptr, tail_ptr, max_ev = struct.unpack(self.HEADER_FORMAT, header)

            if magic != self.MAGIC:
                # Initialize new header
                self.mm[:self.HEADER_SIZE] = struct.pack(self.HEADER_FORMAT, self.MAGIC, self.VERSION, 0, 0, self.max_events)
                self.head_ptr = 0
                self.tail_ptr = 0
            else:
                self.head_ptr = head_ptr
                self.tail_ptr = tail_ptr

    def _update_header(self):
        header_data = struct.pack(self.HEADER_FORMAT, self.MAGIC, self.VERSION, self.head_ptr, self.tail_ptr, self.max_events)
        self.mm[:self.HEADER_SIZE] = header_data

    def subscribe(self, category: int, callback: Callable):
        with self._lock:
            if category not in self._subscribers:
                self._subscribers[category] = []
            self._subscribers[category].append(callback)

    def publish(self, category: int, priority: int = 0, source_hash: int = 0, dest_hash: int = 0, payload_hash: int = 0) -> uuid.UUID:
        with self._lock:
            event_id = uuid.uuid4()
            timestamp = int(time.time() * 1000)

            # Pack event
            record = struct.pack(
                self.RECORD_FORMAT,
                event_id.bytes,
                category,
                EventStatus.PENDING,
                priority,
                0, # retry_count
                timestamp,
                source_hash,
                dest_hash,
                0, # duration
                payload_hash
            )

            # Write to circular buffer
            offset = self.HEADER_SIZE + (self.tail_ptr * self.RECORD_SIZE)
            self.mm[offset:offset+self.RECORD_SIZE] = record

            self.tail_ptr = (self.tail_ptr + 1) % self.max_events
            if self.tail_ptr == self.head_ptr:
                # Buffer full, advance head (overwrite oldest)
                self.head_ptr = (self.head_ptr + 1) % self.max_events

            self._update_header()
            return event_id

    def poll_events(self, limit: int = 10) -> List[Dict]:
        """Poll pending events to dispatch to workers."""
        events = []
        with self._lock:
            count = 0
            ptr = self.head_ptr

            while ptr != self.tail_ptr and count < limit:
                offset = self.HEADER_SIZE + (ptr * self.RECORD_SIZE)
                record_data = self.mm[offset:offset+self.RECORD_SIZE]

                (id_bytes, category, status, priority, retry, ts,
                 src, dst, dur, payload) = struct.unpack(self.RECORD_FORMAT, record_data)

                if status == EventStatus.PENDING:
                    events.append({
                        'id': uuid.UUID(bytes=id_bytes),
                        'category': category,
                        'status': status,
                        'priority': priority,
                        'retry_count': retry,
                        'timestamp': ts,
                        'source_hash': src,
                        'dest_hash': dst,
                        'payload_hash': payload,
                        'ptr_index': ptr # save ptr to update status later
                    })

                    # Mark as processing
                    updated_record = struct.pack(
                        self.RECORD_FORMAT,
                        id_bytes, category, EventStatus.PROCESSING, priority, retry,
                        ts, src, dst, dur, payload
                    )
                    self.mm[offset:offset+self.RECORD_SIZE] = updated_record

                ptr = (ptr + 1) % self.max_events
                count += 1

        return events

    def complete_event(self, ptr_index: int, status: int, duration_ms: int):
        with self._lock:
            offset = self.HEADER_SIZE + (ptr_index * self.RECORD_SIZE)
            record_data = self.mm[offset:offset+self.RECORD_SIZE]

            (id_bytes, category, old_status, priority, retry, ts,
             src, dst, old_dur, payload) = struct.unpack(self.RECORD_FORMAT, record_data)

            updated_record = struct.pack(
                self.RECORD_FORMAT,
                id_bytes, category, status, priority, retry,
                ts, src, dst, duration_ms, payload
            )
            self.mm[offset:offset+self.RECORD_SIZE] = updated_record

    def close(self):
        with self._lock:
            self.mm.close()
            self.fd.close()
