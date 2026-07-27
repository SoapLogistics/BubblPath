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
        if not lesson or not lesson.strip():
            raise ValueError("Lesson cannot be blank or empty")

        if lesson.strip().lower() in ["pass", "fail", "success", "error"]:
            raise ValueError("Lesson cannot be a simple status string")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check for duplicates
            cursor.execute(
                "SELECT 1 FROM memory_atoms WHERE packet_id = ? AND memory_type = ? AND result = ? AND lesson = ?",
                (packet_id, memory, result, lesson)
            )
            if cursor.fetchone() is not None:
                return {"recorded": False, "reason": "duplicate"}

            conn.execute(
                "INSERT INTO memory_atoms (packet_id, memory_type, result, lesson) VALUES (?, ?, ?, ?)",
                (packet_id, memory, result, lesson)
            )

        return {"recorded": True, "packet_id": packet_id, "memory_type": memory, "result": result}
