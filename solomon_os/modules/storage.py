from solomon_os.kernel import SolomonModule
import sqlite3
import threading
import json
import logging

logger = logging.getLogger("StorageModule")

class StorageModule(SolomonModule):
    def __init__(self):
        super().__init__()
        self.db_path = "solomon_vfs.db"
        self._lock = threading.RLock()

    def start(self):
        super().start()
        self._init_db()
        self.kernel.register_rpc('vfs_write', self.vfs_write)
        self.kernel.register_rpc('vfs_read', self.vfs_read)
        self.kernel.register_rpc('vfs_list', self.vfs_list)

    def _init_db(self):
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Enforce WAL mode for concurrency
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vfs (
                    path TEXT PRIMARY KEY,
                    content TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()

    def vfs_write(self, path: str, content: dict) -> bool:
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO vfs (path, content, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (path, json.dumps(content))
                )
                conn.commit()
                conn.close()
                logger.info(f"VFS Write: {path}")
                return True
            except Exception as e:
                logger.error(f"VFS Write failed: {e}")
                return False

    def vfs_read(self, path: str) -> dict:
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT content FROM vfs WHERE path = ?", (path,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    return json.loads(row[0])
                return None
            except Exception as e:
                logger.error(f"VFS Read failed: {e}")
                return None

    def vfs_list(self, prefix: str = "") -> list:
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT path FROM vfs WHERE path LIKE ?", (f"{prefix}%",))
                rows = cursor.fetchall()
                conn.close()
                return [row[0] for row in rows]
            except Exception as e:
                logger.error(f"VFS List failed: {e}")
                return []
