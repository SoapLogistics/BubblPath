# services/solomon_learning_writeback.py
import sqlite3
import os

route_key = "solomon_learning_writeback"

class LearningWriteback:
    def __init__(self, db_path="memory_atoms.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_atoms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    packet_id TEXT,
                    memory_type TEXT,
                    result TEXT,
                    lesson TEXT
                )
            ''')

    def record_lesson(self, packet_id, result, memory, lesson=""):
        # Enforce memory quality: Reject blank or empty lesson content
        if not lesson or not lesson.strip():
            raise ValueError("Lesson content cannot be blank or empty")

        # Raise ValueError on status-only entries (e.g. 'pass', 'fail')
        if lesson.strip().lower() in ["pass", "fail"]:
            raise ValueError("Lesson content cannot be status-only entries like 'pass' or 'fail'")

        # Ensure write idempotency: check for matching rows to prevent duplicate records
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM memory_atoms WHERE packet_id = ? AND memory_type = ? AND result = ? AND lesson = ?",
                (packet_id, memory, result, lesson)
            )
            row = cursor.fetchone()
            if row:
                return {"recorded": True, "packet_id": packet_id, "memory_type": memory, "result": result, "duplicate": True}

            conn.execute(
                "INSERT INTO memory_atoms (packet_id, memory_type, result, lesson) VALUES (?, ?, ?, ?)",
                (packet_id, memory, result, lesson)
            )
        return {"recorded": True, "packet_id": packet_id, "memory_type": memory, "result": result}
