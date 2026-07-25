import sqlite3
import threading
from typing import Optional, List, Dict, Any, Tuple
import json

class DatabaseManager:
    """
    Thread-safe SQLite connection pool manager for Project Solomon.
    Enforces WAL mode to prevent locking issues in a highly concurrent architecture.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = "solomon_vfs.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._init(db_path)
            return cls._instance

    def _init(self, db_path: str):
        self.db_path = db_path
        # Use thread local storage to hold a connection per thread
        self.local = threading.local()
        self._initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self.local, "connection"):
            # isolation_level=None enables autocommit mode, which is generally better
            # for WAL performance if transactions are managed explicitly when needed.
            conn = sqlite3.connect(self.db_path, check_same_thread=False, isolation_level=None)
            conn.row_factory = sqlite3.Row

            # Crucial optimizations for high-concurrency SQLite
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.execute('PRAGMA synchronous=NORMAL;')
            conn.execute('PRAGMA busy_timeout=5000;')  # Wait 5s for lock
            conn.execute('PRAGMA cache_size=-64000;') # 64MB cache

            self.local.connection = conn

        return self.local.connection

    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error executing query {query}: {e}")
            raise

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Executes a write operation (INSERT/UPDATE/DELETE) and returns the lastrowid."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE") # Use IMMEDIATE to acquire write lock early
            cursor.execute(query, params)
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error executing write {query}: {e}")
            raise

    def _initialize_schema(self):
        """Sets up the base schemas for VFS and Memory Cards if they don't exist."""
        # Note: In a production 20-year lifespan app, we'd use a migration tool like Alembic.
        # But per SED (Solomon Efficiency Doctrine), we keep it extremely simple first.

        schema_vfs = """
        CREATE TABLE IF NOT EXISTS vfs_files (
            filepath TEXT PRIMARY KEY,
            content BLOB,
            mime_type TEXT,
            size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hash TEXT
        );
        """

        schema_memory = """
        CREATE TABLE IF NOT EXISTS memory_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            layer TEXT NOT NULL,          -- e.g., 'episodic', 'semantic', 'strategic'
            content TEXT NOT NULL,
            embedding TEXT,               -- JSON serialized vector
            confidence REAL DEFAULT 1.0,
            use_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT                 -- JSON string for provenance, etc.
        );
        """

        schema_raw_experience = """
        CREATE TABLE IF NOT EXISTS raw_experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            input_data TEXT,
            output_data TEXT,
            success BOOLEAN,
            metrics TEXT,                 -- JSON string for tokens, time, etc.
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(schema_vfs)
            cursor.execute(schema_memory)
            cursor.execute(schema_raw_experience)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Schema initialization failed: {e}")
            raise

    def close_all(self):
        """Cleanup method for shutting down gracefully."""
        # Thread locals make this tricky to clean up purely from the manager,
        # but Python usually cleans up SQLite connections nicely on exit.
        pass
