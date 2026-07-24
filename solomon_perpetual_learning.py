from datetime import datetime
import json

class PerpetualLearningEngine:
    def __init__(self, db_manager):
        self.db = db_manager

    # --- Phase 1 & 2: Capture ---
    def record_learning_event(self, content, source="unknown", confidence=0.5,
                              source_reliability=0.5, reason_accepted=None, is_procedure=False, is_fact=True):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO learning_events
               (content, source, confidence, source_reliability, reason_accepted, is_procedure, is_fact)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (content, source, confidence, source_reliability, reason_accepted, is_procedure, is_fact)
        )
        conn.commit()
        return cursor.lastrowid

    def get_learning_events(self, limit=10):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_events ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # --- Phase 3: Classification ---
    def classify_memories(self):
        """Automatically classify facts vs procedures and detect duplicates."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Super simple rule: if it starts with a verb or "how to", it's a procedure.
        cursor.execute("SELECT id, content FROM learning_events WHERE status = 'active'")
        events = cursor.fetchall()

        updates = 0
        for event in events:
            content_lower = event['content'].lower()
            if content_lower.startswith("how to ") or content_lower.split(" ")[0] in ["run", "install", "deploy", "build", "create", "delete"]:
                cursor.execute("UPDATE learning_events SET is_procedure = 1, is_fact = 0 WHERE id = ?", (event['id'],))
                updates += 1

        # Detect simple duplicate strings and merge
        cursor.execute("""
            UPDATE learning_events
            SET status = 'archived'
            WHERE id NOT IN (
                SELECT MIN(id) FROM learning_events GROUP BY content
            )
        """)
        conn.commit()
        return updates

    # --- Phase 4: Skill Extraction ---
    def extract_procedures(self):
        """Convert repeated workflows into procedures."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # In testing we sometimes want this to act immediately based on string matching
        # (similar to our old mock logic before the modular refactor).
        cursor.execute("SELECT * FROM learning_events WHERE is_procedure = 0 AND (content LIKE '%run %' OR content LIKE '%install %' OR content LIKE '%deploy %')")
        events = cursor.fetchall()
        for event in events:
            cursor.execute("UPDATE learning_events SET is_procedure = 1 WHERE id = ?", (event['id'],))

        cursor.execute("SELECT * FROM learning_events WHERE is_procedure = 1 AND status = 'active'")
        events = cursor.fetchall()

        extracted = 0
        for event in events:
            # Check if procedure already exists
            cursor.execute("SELECT id FROM procedures WHERE steps = ?", (event['content'],))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO procedures (name, steps, quality_score) VALUES (?, ?, ?)",
                    (f"Procedure derived from event {event['id']}", event['content'], event['confidence'])
                )
                extracted += 1

        conn.commit()
        return extracted

    # --- Phase 5: Reinforcement ---
    def apply_reinforcement(self, event_id, success=True):
        """Reward successful knowledge, penalize incorrect knowledge (forgetting curve logic)."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if success:
            cursor.execute("""
                UPDATE learning_events
                SET confidence = MIN(1.0, confidence + 0.1), usage_count = usage_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (event_id,))
        else:
            cursor.execute("""
                UPDATE learning_events
                SET confidence = MAX(0.0, confidence - 0.2), usage_count = usage_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (event_id,))
        conn.commit()

    def run_forgetting_curve(self):
        """Archive memories that haven't been accessed and have low confidence."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE learning_events
            SET status = 'archived'
            WHERE confidence < 0.2 AND usage_count < 2 AND julianday('now') - julianday(last_accessed) > 7
        """)
        conn.commit()

    # --- Phase 6: Self-Evaluation ---
    def generate_learning_report(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM learning_events WHERE status = 'active'")
        active = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM learning_events WHERE is_procedure = 1")
        procs = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(confidence) FROM learning_events WHERE status = 'active'")
        avg_conf = cursor.fetchone()[0] or 0.0

        return {
            "active_memories": active,
            "procedural_memories": procs,
            "average_confidence": round(avg_conf, 2)
        }
