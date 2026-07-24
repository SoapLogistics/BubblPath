import sqlite3
import shutil
import os

class DBSnapshotManager:
    """
    Opt 18: Pre-execution SQLite snapshot and restore class.
    Prevents Skill Sandbox from permanently corrupting the active memory database.
    """
    def __init__(self, db_path: str = "solomon_mnemosyne_demo.db"):
        self.db_path = db_path
        self.snapshot_path = f"/tmp/{os.path.basename(db_path)}.snapshot"

    def take_snapshot(self) -> bool:
        try:
            # First force a flush
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(FULL);")
            conn.close()

            shutil.copy2(self.db_path, self.snapshot_path)
            return True
        except Exception as e:
            print(f"Snapshot failed: {e}")
            return False

    def restore_snapshot(self) -> bool:
        if not os.path.exists(self.snapshot_path):
            return False
        try:
            shutil.copy2(self.snapshot_path, self.db_path)
            os.remove(self.snapshot_path)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def cleanup(self):
        if os.path.exists(self.snapshot_path):
            os.remove(self.snapshot_path)
