# services/solomon_learning_writeback.py
import sqlite3
import os

route_key = "solomon_learning_writeback"

class LearningWriteback:
    def __init__(self):
        self.db_path = "memory_atoms.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
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
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            conn.execute(
                "INSERT INTO memory_atoms (packet_id, memory_type, result, lesson) VALUES (?, ?, ?, ?)",
                (packet_id, memory, result, lesson)
            )
        return {"recorded": True, "packet_id": packet_id, "memory_type": memory, "result": result}
