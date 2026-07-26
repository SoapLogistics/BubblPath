import json
import sqlite3

class QResultVerifier:
    def __init__(self, db_path="memory_atoms.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_atoms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    link_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def record_lesson(self, packet_id, lesson_text):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO memory_atoms (memory_type, content, link_id) VALUES (?, ?, ?)",
                         ("lesson", lesson_text, packet_id))

    def record_failure(self, packet_id, error_details):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO memory_atoms (memory_type, content, link_id) VALUES (?, ?, ?)",
                         ("failure", error_details, packet_id))

    def record_repair(self, failure_packet_id, repair_details):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO memory_atoms (memory_type, content, link_id) VALUES (?, ?, ?)",
                         ("repair", repair_details, failure_packet_id))

    def get_recalled_memories(self, context=""):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT memory_type, content FROM memory_atoms ORDER BY timestamp DESC LIMIT 5")
            return [{"type": row[0], "content": row[1]} for row in cur.fetchall()]

    def verify(self, packet, test_result):
        if test_result.get("status") == "pass":
            self.record_lesson(packet["id"], f"Passed verification for {packet['id']}")
        elif test_result.get("status") == "fail":
            self.record_failure(packet["id"], test_result.get("error", "Unknown error"))

    def inject_preface(self, packet):
        memories = self.get_recalled_memories(packet.get("context", ""))
        packet["preface"] = memories
        return packet
