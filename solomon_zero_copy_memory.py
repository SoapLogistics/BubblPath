import os
import mmap
import struct
import time
import math
from typing import Dict, List, Tuple, Optional

# Memory structure per node:
# [id: int (4 bytes)] [valence: float (4 bytes)] [arousal: float (4 bytes)] [timestamp: double (8 bytes)] [active: int (1 byte)]
NODE_FMT = '=i f f d b'
NODE_SIZE = struct.calcsize(NODE_FMT)
MAX_NODES = 10000

class ZeroCopyMemorySubstrate:
    """
    Zero-Copy Memory Substrate utilizing mmap and struct.
    Implements extremely fast, zero-copy binary serialization mimicking human memory,
    with emotional tagging (valence/arousal) and connectome pruning.
    """
    def __init__(self, filename: str = "solomon_brain_map.bin", max_nodes: int = MAX_NODES):
        self.filename = filename
        self.max_nodes = max_nodes
        self.file_size = self.max_nodes * NODE_SIZE

        # Ensure file exists and is of correct size
        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.write(b'\x00' * self.file_size)
        else:
            current_size = os.path.getsize(self.filename)
            if current_size < self.file_size:
                with open(self.filename, 'ab') as f:
                    f.write(b'\x00' * (self.file_size - current_size))

        self.f = open(self.filename, 'r+b')
        self.m = mmap.mmap(self.f.fileno(), self.file_size)

        # In-memory index to map logical IDs to physical slots
        self.slot_map: Dict[int, int] = {}
        self._build_index()

    def _build_index(self):
        """Scans the memory map to build the slot index."""
        for i in range(self.max_nodes):
            offset = i * NODE_SIZE
            data = self.m[offset:offset + NODE_SIZE]
            node_id, valence, arousal, timestamp, active = struct.unpack(NODE_FMT, data)
            if active == 1:
                self.slot_map[node_id] = i

    def _find_free_slot(self) -> Optional[int]:
        """Finds the first inactive slot."""
        for i in range(self.max_nodes):
            offset = i * NODE_SIZE
            # Just read the active byte
            active = self.m[offset + NODE_SIZE - 1]
            if active == 0:
                return i
        return None

    def store_memory(self, node_id: int, valence: float, arousal: float) -> bool:
        """Stores or updates a memory node with emotional tagging."""
        timestamp = time.time()

        if node_id in self.slot_map:
            slot = self.slot_map[node_id]
        else:
            slot = self._find_free_slot()
            if slot is None:
                self.prune_connectome() # Trigger pruning if full
                slot = self._find_free_slot()
                if slot is None:
                    return False # Still full
            self.slot_map[node_id] = slot

        offset = slot * NODE_SIZE
        packed = struct.pack(NODE_FMT, node_id, valence, arousal, timestamp, 1)
        self.m[offset:offset + NODE_SIZE] = packed
        return True

    def retrieve_memory(self, node_id: int) -> Optional[Tuple[float, float, float]]:
        """Retrieves a memory node (valence, arousal, timestamp)."""
        if node_id not in self.slot_map:
            return None
        slot = self.slot_map[node_id]
        offset = slot * NODE_SIZE
        data = self.m[offset:offset + NODE_SIZE]
        _, valence, arousal, timestamp, active = struct.unpack(NODE_FMT, data)
        if active == 1:
            return (valence, arousal, timestamp)
        return None

    def prune_connectome(self, threshold_age: float = 86400.0 * 30):
        """
        Connectome pruning: Deactivates memory nodes older than threshold_age
        and with low emotional resonance (valence/arousal magnitude).
        """
        current_time = time.time()
        deactivated = 0
        for node_id, slot in list(self.slot_map.items()):
            offset = slot * NODE_SIZE
            data = self.m[offset:offset + NODE_SIZE]
            _, valence, arousal, timestamp, active = struct.unpack(NODE_FMT, data)

            age = current_time - timestamp
            emotional_resonance = math.sqrt(valence**2 + arousal**2)

            # Prune if old and has low emotional resonance
            if age > threshold_age and emotional_resonance < 0.5:
                # Set active to 0
                self.m[offset + NODE_SIZE - 1] = 0
                del self.slot_map[node_id]
                deactivated += 1

        return deactivated

    def close(self):
        self.m.flush()
        self.m.close()
        self.f.close()
