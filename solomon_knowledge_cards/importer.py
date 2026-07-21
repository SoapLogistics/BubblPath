import os
import re
import json
from datetime import datetime
from .models import DatabaseManager

class DoctrineImporter:
    """
    Imports procedural doctrine files from openclaw-workspace/checklists/
    and registers them as ACTIVE, APPROVED knowledge cards in the Mnemosyne DB.
    Performs duplicate prevention by checking existing card IDs.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def import_directory(self, directory_path: str) -> int:
        """Scans the directory for markdown files and imports them safely."""
        if not os.path.exists(directory_path):
            return 0

        imported_count = 0
        conn = self.db.get_connection()
        try:
            for filename in os.listdir(directory_path):
                if not filename.endswith(".md"):
                    continue

                filepath = os.path.join(directory_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse metadata using regex patterns
                card_id_match = re.search(r"-\s+\*\*Card ID:\*\* ([\w\-]+)", content)
                title_match = re.search(r"# (?:PROCEDURE CARD|MASTER PROCEDURE CARD):\s*(.*)", content)
                focus_match = re.search(r"-\s+\*\*Focus Area:\*\* (.*)", content)

                card_id = card_id_match.group(1).strip() if card_id_match else f"PC-{os.path.splitext(filename)[0].upper()}"
                title = title_match.group(1).strip() if title_match else f"Procedure for {os.path.splitext(filename)[0]}"
                summary = focus_match.group(1).strip() if focus_match else "Procedural checklist doctrine."
                body = content.strip()

                # Check if card ID already exists to prevent duplicate imports
                cursor = conn.execute("SELECT card_id FROM knowledge_cards WHERE card_id = ?", (card_id,))
                if cursor.fetchone():
                    continue

                # Insert the doctrine as an APPROVED and ACTIVE card
                with conn:
                    conn.execute("""
                        INSERT INTO knowledge_cards (
                            card_id, card_type, title, summary, body, confidence,
                            validation_state, security_classification, source_ids,
                            created_at, updated_at
                        ) VALUES (?, 'PROCEDURE', ?, ?, ?, 1.0, 'ACTIVE', 'INTERNAL', '[]', ?, ?);
                    """, (
                        card_id,
                        title,
                        summary,
                        body,
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat()
                    ))

                    # Insert initial revision
                    conn.execute("""
                        INSERT INTO revisions (
                            card_id, version, title, summary, body, confidence,
                            validation_state, security_classification, modifier, reason, created_at
                        ) VALUES (?, 1, ?, ?, ?, 1.0, 'ACTIVE', 'INTERNAL', 'DoctrineImporter', 'Automated import of workspace doctrine.', ?);
                    """, (
                        card_id,
                        title,
                        summary,
                        body,
                        datetime.utcnow().isoformat()
                    ))
                imported_count += 1
        finally:
            conn.close()

        return imported_count
