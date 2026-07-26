import datetime
import threading
import sqlite3
import shutil
import os
import time
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    _instance = None
    _init_lock = threading.Lock()

    def __new__(cls, db_path: str = "solomon_soss.db"):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._init_instance(db_path)
            return cls._instance

    def _init_instance(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")  # WAL mode
        conn.execute("PRAGMA busy_timeout = 10000;")  # 10 seconds busy timeout
        return conn

    def _backup_db(self):
        """Creates a backup before destructive operations or migrations."""
        if os.path.exists(self.db_path):
            backup_path = f"{self.db_path}.{int(time.time())}.bak"
            shutil.copy2(self.db_path, backup_path)

    def _init_db(self) -> None:
        """Runs migrations to initialize the schema."""
        with self._lock:
            self._backup_db()
            conn = self._get_connection()
            try:
                # Migration tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    );
                """)
                conn.commit()

                # Read current version
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_version")
                row = cursor.fetchone()
                current_version = row[0] if row[0] is not None else 0

                # Migration 1: Initial unified schema stub
                if current_version < 1:
                    with conn:
                        # Create tables based on data ownership matrix here if needed
                        conn.execute(
                            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                            (1, datetime.datetime.now(datetime.UTC).isoformat())
                        )

                # Integrity check after migration
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                if result[0] != "ok":
                    raise sqlite3.IntegrityError(f"Database integrity check failed: {result[0]}")
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def execute_read(self, query: str, parameters: Tuple = ()) -> List[sqlite3.Row]:
        """Executes a read query using parameterized SQL."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(query, parameters)
                return cursor.fetchall()
            finally:
                conn.close()

    def execute_write(self, query: str, parameters: Tuple = ()) -> None:
        """Executes a write query within a transaction boundary."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                cursor = conn.cursor()
                cursor.execute(query, parameters)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
