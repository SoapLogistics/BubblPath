import sqlite3
import json
import threading
from typing import Dict, Any, Optional, List

class TaskQueue:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    def enqueue(self, task_type: str, payload: Dict[str, Any]) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO task_queue (task_type, payload)
            VALUES (?, ?)
        ''', (task_type, json.dumps(payload)))
        conn.commit()
        return cursor.lastrowid

    def dequeue(self) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor()

        # BEGIN EXCLUSIVE prevents race conditions across multiple docker workers
        cursor.execute('BEGIN EXCLUSIVE')

        try:
            cursor.execute('''
                SELECT id, task_type, payload
                FROM task_queue
                WHERE status = 'PENDING'
                ORDER BY created_at ASC
                LIMIT 1
            ''')
            row = cursor.fetchone()

            if row:
                cursor.execute('''
                    UPDATE task_queue
                    SET status = 'PROCESSING', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (row['id'],))
                conn.commit()
                return {
                    "id": row['id'],
                    "task_type": row['task_type'],
                    "payload": json.loads(row['payload'])
                }
            else:
                conn.rollback()
                return None
        except Exception as e:
            conn.rollback()
            raise e

    def mark_completed(self, task_id: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE task_queue
            SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))
        conn.commit()

    def mark_failed(self, task_id: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE task_queue
            SET status = 'FAILED', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))
        conn.commit()
