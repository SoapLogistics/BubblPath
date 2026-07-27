import time
import uuid
import sqlite3
import threading
from typing import Optional, Dict, Any


class TokenBucketThrottler:
    def __init__(self, rate: int = 10, capacity: int = 10):
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_fill = time.time()

    def consume(self, tokens_needed: float = 1.0) -> bool:
        now = time.time()
        # Refill tokens based on time elapsed
        elapsed = now - self.last_fill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_fill = now
        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False

class RenewableWorkerLease:
    """
    A worker temporarily owns a task by renewing a timed lease.
    If it disappears, the lease expires and another worker may recover the task.
    Supports a full Multi-Agent Kanban/Task board queue.
    """
    def __init__(self, db_path: str = ":memory:", lease_duration_sec: int = 2):
        self.db_path = db_path
        self.lease_duration_sec = lease_duration_sec
        # Maintain a persistent connection to keep in-memory DB alive
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    payload TEXT,
                    status TEXT,
                    leased_by TEXT,
                    lease_expires_at REAL
                )
            """)
            self.conn.commit()

    def add_task(self, task_id: str, payload: str):
        with self.lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO tasks (task_id, payload, status, leased_by, lease_expires_at) VALUES (?, ?, 'pending', NULL, 0.0)",
                (task_id, payload)
            )
            self.conn.commit()

    def claim_task(self, worker_id: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        with self.lock:
            self.conn.row_factory = sqlite3.Row
            # Claim pending or expired tasks
            cursor = self.conn.execute(
                "SELECT * FROM tasks WHERE status = 'pending' OR (status = 'active' AND lease_expires_at < ?) LIMIT 1",
                (now,)
            )
            row = cursor.fetchone()
            if row:
                task_id = row["task_id"]
                expires_at = now + self.lease_duration_sec
                self.conn.execute(
                    "UPDATE tasks SET status = 'active', leased_by = ?, lease_expires_at = ? WHERE task_id = ?",
                    (worker_id, expires_at, task_id)
                )
                self.conn.commit()
                return {"task_id": task_id, "payload": row["payload"], "lease_expires_at": expires_at}
            return None

    def renew_lease(self, task_id: str, worker_id: str) -> bool:
        now = time.time()
        with self.lock:
            cursor = self.conn.execute(
                "UPDATE tasks SET lease_expires_at = ? WHERE task_id = ? AND leased_by = ? AND status = 'active' AND lease_expires_at >= ?",
                (now + self.lease_duration_sec, task_id, worker_id, now)
            )
            self.conn.commit()
            return cursor.rowcount > 0

    def complete_task(self, task_id: str, worker_id: str) -> bool:
        now = time.time()
        with self.lock:
            cursor = self.conn.execute(
                "UPDATE tasks SET status = 'completed', leased_by = NULL, lease_expires_at = 0.0 WHERE task_id = ? AND leased_by = ? AND lease_expires_at >= ?",
                (task_id, worker_id, now)
            )
            self.conn.commit()
            return cursor.rowcount > 0

    def get_task_status(self, task_id: str) -> Optional[str]:
        with self.lock:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            return row["status"] if row else None
