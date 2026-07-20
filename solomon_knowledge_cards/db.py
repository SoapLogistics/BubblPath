import sqlite3
import json
import os
import datetime
from typing import List, Dict, Any, Optional
from solomon_knowledge_cards.models import KnowledgeCardModel

class SQLiteDatabase:
    def __init__(self, db_path: str = "solomon_cards.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")  # High concurrency
        return conn

    def _init_db(self) -> None:
        """Initializes schema tables and indexes."""
        with self._get_connection() as conn:
            # Cards Master Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    card_id TEXT PRIMARY KEY,
                    card_type TEXT NOT NULL,
                    schema_version TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    body TEXT,
                    status TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    validation_state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_ids TEXT,             -- JSON List
                    parent_card_ids TEXT,        -- JSON List
                    related_card_ids TEXT,       -- JSON List
                    tags TEXT,                   -- JSON List
                    security_classification TEXT NOT NULL,
                    evidence TEXT,
                    supersedes TEXT,
                    superseded_by TEXT,
                    metadata TEXT,               -- JSON Dict
                    why_created TEXT,
                    problem_solved TEXT,
                    future_work_dependent TEXT
                );
            """)

            # Revision History Table (Auditing)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS card_revisions (
                    revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    body TEXT,
                    status TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    validation_state TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY(card_id) REFERENCES cards(card_id) ON DELETE CASCADE
                );
            """)

            # Tag Index (To enable fast sparse searching on tags)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(card_type);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_status ON cards(status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_tags ON cards(tags);")
            conn.commit()

    def save_card(self, card: KnowledgeCardModel, actor: str = "SYSTEM") -> None:
        """Atomic upsert of a Knowledge Card with automated revision logging."""
        card.validate()
        card_data = card.to_dict()

        # Convert list and dict structures to JSON strings
        source_ids_str = json.dumps(card_data["source_ids"])
        parent_card_ids_str = json.dumps(card_data["parent_card_ids"])
        related_card_ids_str = json.dumps(card_data["related_card_ids"])
        tags_str = json.dumps(card_data["tags"])
        metadata_str = json.dumps(card_data["metadata"])

        now = datetime.datetime.utcnow().isoformat() + "Z"
        card_data["updated_at"] = now

        with self._get_connection() as conn:
            # Check if card exists
            cursor = conn.cursor()
            cursor.execute("SELECT schema_version, title, summary, body, status, confidence, validation_state, metadata FROM cards WHERE card_id = ?", (card.card_id,))
            row = cursor.fetchone()

            if row:
                # Upsert Cards Master
                conn.execute("""
                    UPDATE cards SET
                        card_type = ?, schema_version = ?, title = ?, summary = ?, body = ?,
                        status = ?, confidence = ?, validation_state = ?, updated_at = ?,
                        created_by = ?, source_type = ?, source_ids = ?, parent_card_ids = ?,
                        related_card_ids = ?, tags = ?, security_classification = ?,
                        evidence = ?, supersedes = ?, superseded_by = ?, metadata = ?,
                        why_created = ?, problem_solved = ?, future_work_dependent = ?
                    WHERE card_id = ?
                """, (
                    card.card_type, card.schema_version, card.title, card.summary, card.body,
                    card.status, card.confidence, card.validation_state, now,
                    card.created_by, card.source_type, source_ids_str, parent_card_ids_str,
                    related_card_ids_str, tags_str, card.security_classification,
                    card.evidence, card.supersedes, card.superseded_by, metadata_str,
                    card.why_created, card.problem_solved, card.future_work_dependent,
                    card.card_id
                ))
            else:
                # Insert Cards Master
                conn.execute("""
                    INSERT INTO cards (
                        card_id, card_type, schema_version, title, summary, body,
                        status, confidence, validation_state, created_at, updated_at,
                        created_by, source_type, source_ids, parent_card_ids,
                        related_card_ids, tags, security_classification, evidence,
                        supersedes, superseded_by, metadata, why_created, problem_solved, future_work_dependent
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    card.card_id, card.card_type, card.schema_version, card.title, card.summary, card.body,
                    card.status, card.confidence, card.validation_state, card.created_at, now,
                    card.created_by, card.source_type, source_ids_str, parent_card_ids_str,
                    related_card_ids_str, tags_str, card.security_classification, card.evidence,
                    card.supersedes, card.superseded_by, metadata_str, card.why_created, card.problem_solved, card.future_work_dependent
                ))

            # Record Revision history entry
            conn.execute("""
                INSERT INTO card_revisions (
                    card_id, version, title, summary, body, status, confidence,
                    validation_state, updated_at, updated_by, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card.card_id, card.schema_version, card.title, card.summary, card.body,
                card.status, card.confidence, card.validation_state, now, actor, metadata_str
            ))
            conn.commit()

    def get_card(self, card_id: str) -> Optional[KnowledgeCardModel]:
        """Fetch a specific Knowledge Card by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_model(row)

    def delete_card(self, card_id: str) -> None:
        """Soft delete card (marking status as ARCHIVED) to preserve audit trails."""
        with self._get_connection() as conn:
            conn.execute("UPDATE cards SET status = 'ARCHIVED', updated_at = ? WHERE card_id = ?", (
                datetime.datetime.utcnow().isoformat() + "Z", card_id
            ))
            conn.commit()

    def list_all_cards(self) -> List[KnowledgeCardModel]:
        """Retrieve all active cards (excluding ARCHIVED)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cards WHERE status != 'ARCHIVED'")
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def get_revision_history(self, card_id: str) -> List[Dict[str, Any]]:
        """Fetch full revision audit trail for a specific card."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM card_revisions WHERE card_id = ? ORDER BY revision_id DESC", (card_id,))
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    "revision_id": row["revision_id"],
                    "card_id": row["card_id"],
                    "version": row["version"],
                    "title": row["title"],
                    "summary": row["summary"],
                    "body": row["body"],
                    "status": row["status"],
                    "confidence": row["confidence"],
                    "validation_state": row["validation_state"],
                    "updated_at": row["updated_at"],
                    "updated_by": row["updated_by"],
                    "metadata": json.loads(row["metadata"] or "{}")
                })
            return history

    def export_to_jsonl(self, filepath: str) -> None:
        """Backup database cards cleanly to JSON Lines (JSONL) format."""
        cards = self.list_all_cards()
        with open(filepath, "w", encoding="utf-8") as f:
            for card in cards:
                f.write(json.dumps(card.to_dict()) + "\n")

    def import_from_jsonl(self, filepath: str) -> None:
        """Restore cards from a JSONL backup file without destroying historical data."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found at: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    card = KnowledgeCardModel.from_dict(data)
                    self.save_card(card, actor="BACKUP_IMPORT")

    def _row_to_model(self, row: sqlite3.Row) -> KnowledgeCardModel:
        return KnowledgeCardModel(
            card_id=row["card_id"],
            card_type=row["card_type"],
            schema_version=row["schema_version"],
            title=row["title"],
            summary=row["summary"],
            body=row["body"],
            status=row["status"],
            confidence=row["confidence"],
            validation_state=row["validation_state"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            created_by=row["created_by"],
            source_type=row["source_type"],
            source_ids=json.loads(row["source_ids"] or "[]"),
            parent_card_ids=json.loads(row["parent_card_ids"] or "[]"),
            related_card_ids=json.loads(row["related_card_ids"] or "[]"),
            tags=json.loads(row["tags"] or "[]"),
            security_classification=row["security_classification"],
            evidence=row["evidence"],
            supersedes=row["supersedes"],
            superseded_by=row["superseded_by"],
            metadata=json.loads(row["metadata"] or "{}"),
            why_created=row["why_created"],
            problem_solved=row["problem_solved"],
            future_work_dependent=row["future_work_dependent"]
        )
