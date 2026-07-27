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
                    lesson TEXT,
                    confidence REAL,
                    utility REAL
                )
            ''')

    def record_lesson(self, packet_id, result, memory, lesson=""):
        # 1. Validation checks (reject empty lessons)
        if not lesson or not lesson.strip():
            raise ValueError("Lesson content cannot be empty")

        # 2. Reject status-only words
        clean_lesson = lesson.strip().lower()
        if clean_lesson in ["pass", "fail", "success", "unknown", "error", "none", ""]:
            raise ValueError("Lesson content cannot be a status-only word")

        # 3. Idempotency checks (prevent duplicate entries)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM memory_atoms WHERE packet_id=? AND memory_type=? AND result=? AND lesson=?",
                (packet_id, memory, result, lesson)
            )
            row = cursor.fetchone()
            if row:
                # Return the existing entry cleanly instead of appending a duplicate
                return {
                    "recorded": True,
                    "packet_id": packet_id,
                    "memory_type": memory,
                    "result": result,
                    "duplicate": True
                }

            # Insert with initial scoring
            cursor.execute(
                "INSERT INTO memory_atoms (packet_id, memory_type, result, lesson, confidence, utility) VALUES (?, ?, ?, ?, 1.0, 1.0)",
                (packet_id, memory, result, lesson)
            )
            conn.commit()

        return {"recorded": True, "packet_id": packet_id, "memory_type": memory, "result": result, "duplicate": False}
