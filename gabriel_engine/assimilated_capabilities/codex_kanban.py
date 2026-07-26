import time
import uuid
from typing import Optional, Dict, Any
from core.solomon_knowledge_cards.storage.db import DatabaseManager

class RenewableWorkerLease:
    """
    A worker temporarily owns a task by renewing a timed lease.
    If it disappears, the lease expires and another worker may recover the task.
    Supports a full Multi-Agent Kanban/Task board queue.
    """
    def __init__(self, db_path: str = "solomon_soss.db", lease_duration_sec: int = 10):
        self.db = DatabaseManager(db_path)
        self.lease_duration_sec = lease_duration_sec

    def add_task(self, task_id: str, payload: str):
        self.db.execute_write(
            "INSERT OR REPLACE INTO tasks (task_id, payload, status, leased_by, lease_expires_at) VALUES (?, ?, 'pending', NULL, 0.0)",
            (task_id, payload)
        )

    def claim_task(self, worker_id: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        # Claim pending or expired tasks
        rows = self.db.execute_read(
            "SELECT * FROM tasks WHERE status = 'pending' OR (status = 'active' AND lease_expires_at < ?) LIMIT 1",
            (now,)
        )
        if rows:
            row = rows[0]
            task_id = row["task_id"]
            expires_at = now + self.lease_duration_sec
            self.db.execute_write(
                "UPDATE tasks SET status = 'active', leased_by = ?, lease_expires_at = ? WHERE task_id = ?",
                (worker_id, expires_at, task_id)
            )
            return {"task_id": task_id, "payload": row["payload"], "lease_expires_at": expires_at}
        return None

    def renew_lease(self, task_id: str, worker_id: str) -> bool:
        now = time.time()
        rowcount = self.db.execute_write(
            "UPDATE tasks SET lease_expires_at = ? WHERE task_id = ? AND leased_by = ? AND status = 'active' AND lease_expires_at >= ?",
            (now + self.lease_duration_sec, task_id, worker_id, now)
        )
        return rowcount > 0

    def complete_task(self, task_id: str, worker_id: str) -> bool:
        now = time.time()
        rowcount = self.db.execute_write(
            "UPDATE tasks SET status = 'completed', leased_by = NULL, lease_expires_at = 0.0 WHERE task_id = ? AND leased_by = ? AND lease_expires_at >= ?",
            (task_id, worker_id, now)
        )
        return rowcount > 0

    def get_task_status(self, task_id: str) -> Optional[str]:
        rows = self.db.execute_read("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
        return rows[0]["status"] if rows else None
