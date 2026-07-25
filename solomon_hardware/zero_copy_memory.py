import mmap
import struct
import os

class ZeroCopyMemoryMap:
    """
    Implements true zero-copy O(1) loading by mapping a binary file directly into
    memory using `mmap`. Memory graph nodes are packed as raw C structs.
    """
    # Struct format:
    # int id (4 bytes), float weight (4 bytes), float state (4 bytes), padding (52 bytes)
    # Total: 64 bytes per node (perfect L1 cache alignment)
    STRUCT_FMT = 'i f f 52x'
    RECORD_SIZE = struct.calcsize(STRUCT_FMT)

    def __init__(self, filepath="gabriel_knowledge_base.bin", initial_records=1000):
        self.filepath = filepath
        self.capacity = initial_records
        self.file_size = self.capacity * self.RECORD_SIZE

        self._ensure_file_exists()

        self.file_obj = open(self.filepath, "r+b")
        self.mmap_obj = mmap.mmap(self.file_obj.fileno(), self.file_size)

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) != self.file_size:
            with open(self.filepath, "wb") as f:
                f.write(b'\x00' * self.file_size)

    def write_node(self, index: int, node_id: int, weight: float, state: float):
        if index < 0 or index >= self.capacity:
            raise IndexError("Index out of bounds")
        packed_data = struct.pack(self.STRUCT_FMT, node_id, weight, state)
        offset = index * self.RECORD_SIZE
        self.mmap_obj[offset:offset+self.RECORD_SIZE] = packed_data

    def read_node(self, index: int) -> dict:
        if index < 0 or index >= self.capacity:
            raise IndexError("Index out of bounds")
        offset = index * self.RECORD_SIZE
        packed_data = self.mmap_obj[offset:offset+self.RECORD_SIZE]
        node_id, weight, state = struct.unpack(self.STRUCT_FMT, packed_data)
        return {"id": node_id, "weight": weight, "state": state}

    def close(self):
        self.mmap_obj.close()
        self.file_obj.close()

if __name__ == '__main__':
    mem = ZeroCopyMemoryMap()
    mem.write_node(0, 42, 0.95, -0.45)
    print("Zero-Copy Node 0:", mem.read_node(0))
    mem.close()
