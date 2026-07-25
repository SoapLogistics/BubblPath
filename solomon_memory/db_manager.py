import sqlite3
import threading
import logging
from contextlib import contextmanager

logger = logging.getLogger("MnemosyneDB")

class DatabaseManager:
    """
    Thread-safe connection pool manager for Solomon's SQLite databases.
    Enforces WAL mode to prevent locking across the asynchronous architecture.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = "cognitive_architecture.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance.db_path = db_path
                cls._instance.local = threading.local()
        return cls._instance

    def _get_connection(self) -> sqlite3.Connection:
        """Retrieves a thread-local SQLite connection with WAL enabled."""
        if not hasattr(self.local, "connection"):
            logger.debug(f"Opening new DB connection to {self.db_path} for thread {threading.get_ident()}")
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enforce WAL (Write-Ahead Logging) for high concurrency
            conn.execute("PRAGMA journal_mode=WAL;")
            # Wait up to 5 seconds before throwing a 'database is locked' error
            conn.execute("PRAGMA busy_timeout=5000;")
            self.local.connection = conn
        return self.local.connection

    @contextmanager
    def get_cursor(self):
        """Context manager yielding a database cursor that auto-commits or rolls back."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            cursor.close()

    def execute_query(self, query: str, params: tuple = ()) -> None:
        """Utility for one-off write operations."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """Utility for one-off read operations."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
