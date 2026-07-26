import os
import struct
import mmap
import time
import threading
from typing import Dict, List, Optional, Any

# Registry metadata
route_key = "solomon_capability_registry"

class CapabilityRegistry:
    """
    Hyper-efficient, zero-copy Capability Registry using memory-mapped files.
    Enforces O(1) bounded access, dynamic discovery, and dependency validation.
    """

    # Record Layout (1024 bytes aligned)
    # ? : valid flag (1)
    # 32s : Unique Identifier (32)
    # 64s : Human-readable Name (64)
    # 128s : Module Path (128)
    # 16s : Version (16)
    # 32s : Owner (32)
    # 128s : Description (128)
    # 128s : Inputs (128)
    # 128s : Outputs (128)
    # 64s : Required Permissions (64)
    # 128s : Dependencies (128)
    # 16s : Health State (16)
    # 4s : SS Classification (4)
    # d : Last Validation Time (8)
    # 147x : Padding (147)
    # Total: 1 + 32 + 64 + 128 + 16 + 32 + 128 + 128 + 128 + 64 + 128 + 16 + 4 + 8 + 147 = 1024

    RECORD_FORMAT = "<? 32s 64s 128s 16s 32s 128s 128s 128s 64s 128s 16s 4s d 147x"
    RECORD_SIZE = 1024
    MAX_CAPABILITIES = 4096
    FILE_SIZE = RECORD_SIZE * MAX_CAPABILITIES

    def __init__(self, filepath: str = "capability_registry.bin"):
        self.filepath = filepath
        self._lock = threading.RLock()
        self.mmap_obj = None
        self.fd = None

        # In-memory O(1) lookup map (Identifier -> Offset)
        self._index: Dict[str, int] = {}

        self._initialize_mmap()

    def _initialize_mmap(self):
        with self._lock:
            file_exists = os.path.exists(self.filepath)

            # Open file and ensure size
            self.fd = open(self.filepath, "a+b")
            if not file_exists or os.path.getsize(self.filepath) != self.FILE_SIZE:
                self.fd.truncate(self.FILE_SIZE)

            self.fd.flush()
            self.mmap_obj = mmap.mmap(self.fd.fileno(), self.FILE_SIZE, access=mmap.ACCESS_WRITE)

            self._rebuild_index()

    def _rebuild_index(self):
        """Rebuilds the O(1) lookup table from the memory mapped file."""
        self._index.clear()
        for offset in range(0, self.FILE_SIZE, self.RECORD_SIZE):
            valid = struct.unpack_from('?', self.mmap_obj, offset)[0]
            if valid:
                record = struct.unpack_from(self.RECORD_FORMAT, self.mmap_obj, offset)
                uid = record[1].rstrip(b'\x00').decode('utf-8', errors='ignore')
                if uid:
                    self._index[uid] = offset

    def close(self):
        """Safely closes the memory mapped file."""
        with self._lock:
            if self.mmap_obj:
                self.mmap_obj.flush()
                self.mmap_obj.close()
                self.mmap_obj = None
            if self.fd:
                self.fd.close()
                self.fd = None

    def _find_free_offset(self) -> int:
        """Finds the first available offset for a new record in O(N) time bounded by MAX_CAPABILITIES."""
        for offset in range(0, self.FILE_SIZE, self.RECORD_SIZE):
            valid = struct.unpack_from('?', self.mmap_obj, offset)[0]
            if not valid:
                return offset
        raise MemoryError("Capability Registry has reached maximum capacity.")

    def _encode_str(self, s: str, size: int) -> bytes:
        return s.encode('utf-8')[:size].ljust(size, b'\x00')

    def register_capability(self,
                            uid: str,
                            name: str,
                            module_path: str,
                            version: str,
                            owner: str,
                            description: str,
                            inputs: str,
                            outputs: str,
                            permissions: str,
                            dependencies: str, # comma-separated uids
                            health_state: str,
                            ss_class: str,
                            force_update: bool = False) -> bool:
        """Registers or updates a capability with zero-copy binary layout."""
        with self._lock:
            # Check dependency rules: missing dependencies block activation
            if dependencies:
                deps_list = [d.strip() for d in dependencies.split(",") if d.strip()]
                for dep in deps_list:
                    if dep not in self._index:
                        raise ValueError(f"Missing dependency: {dep}")

            # Check duplicate registrations
            if uid in self._index:
                if not force_update:
                    raise ValueError(f"Capability already registered: {uid}")
                offset = self._index[uid]
            else:
                offset = self._find_free_offset()

            # Pack record
            last_validation_time = time.time()
            struct.pack_into(
                self.RECORD_FORMAT,
                self.mmap_obj,
                offset,
                True, # valid
                self._encode_str(uid, 32),
                self._encode_str(name, 64),
                self._encode_str(module_path, 128),
                self._encode_str(version, 16),
                self._encode_str(owner, 32),
                self._encode_str(description, 128),
                self._encode_str(inputs, 128),
                self._encode_str(outputs, 128),
                self._encode_str(permissions, 64),
                self._encode_str(dependencies, 128),
                self._encode_str(health_state, 16),
                self._encode_str(ss_class, 4),
                last_validation_time
            )

            self._index[uid] = offset
            return True

    def get_capability(self, uid: str) -> Optional[Dict[str, Any]]:
        """Retrieves a capability with O(1) performance."""
        with self._lock:
            if uid not in self._index:
                return None

            offset = self._index[uid]
            record = struct.unpack_from(self.RECORD_FORMAT, self.mmap_obj, offset)

            if not record[0]: # Not valid
                return None

            return {
                "uid": record[1].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "name": record[2].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "module_path": record[3].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "version": record[4].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "owner": record[5].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "description": record[6].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "inputs": record[7].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "outputs": record[8].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "permissions": record[9].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "dependencies": record[10].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "health_state": record[11].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "ss_class": record[12].rstrip(b'\x00').decode('utf-8', errors='ignore'),
                "last_validation_time": record[13]
            }

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """Lists all valid capabilities."""
        with self._lock:
            capabilities = []
            for uid in self._index.keys():
                cap = self.get_capability(uid)
                if cap:
                    capabilities.append(cap)
            return capabilities

    def remove_capability(self, uid: str) -> bool:
        """Removes a capability (mark as invalid)."""
        with self._lock:
            if uid not in self._index:
                return False

            offset = self._index[uid]
            # Set valid flag to False
            struct.pack_into('?', self.mmap_obj, offset, False)

            del self._index[uid]
            return True
