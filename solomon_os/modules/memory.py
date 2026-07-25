from solomon_os.kernel import SolomonModule
import logging

logger = logging.getLogger("MemoryModule")

class MemoryModule(SolomonModule):
    def start(self):
        super().start()
        # Initialize Memory (SOK, vectors, graph)
        self.kernel.register_rpc('memory_store', self.store)
        self.kernel.register_rpc('memory_retrieve', self.retrieve)

    def store(self, key: str, value: dict) -> bool:
        """Stores memory objects using the VFS as a paging mechanism."""
        vfs_path = f"/sys/memory/{key}"
        try:
            # We call the VFS via the kernel RPC to decouple modules
            success = self.kernel.call_rpc('vfs_write', vfs_path, value)
            if success:
                logger.info(f"Paged memory to VFS: {vfs_path}")
                # Publish an event that memory was updated
                self.kernel.publish('MEMORY_UPDATED', self.name, {"key": key, "vfs_path": vfs_path})
            return success
        except Exception as e:
            logger.error(f"Failed to page memory {key} to VFS: {e}")
            return False

    def retrieve(self, key: str) -> dict:
        """Retrieves memory objects paged in the VFS."""
        vfs_path = f"/sys/memory/{key}"
        try:
            data = self.kernel.call_rpc('vfs_read', vfs_path)
            if data:
                logger.info(f"Loaded memory from VFS: {vfs_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to retrieve memory {key} from VFS: {e}")
            return None
