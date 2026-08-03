import datetime
import json
import os
import sqlite3
import threading
from typing import Any

from solomon_knowledge_cards.models.card import KnowledgeCard


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 10000;")  # 10 seconds busy timeout
        return conn

    def _init_db(self) -> None:
        """Runs migrations to initialize the schema."""
        with self._lock:
            conn = self._get_connection()
            try:
                # Migration tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    );
                """)
                conn.commit()

                # Read current version
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_version")
                row = cursor.fetchone()
                current_version = row[0] if row[0] is not None else 0

                # Migration 1: Initial schema
                if current_version < 1:
                    with conn:
                        conn.execute("""
                            CREATE TABLE cards (
                                card_id TEXT PRIMARY KEY,
                                card_type TEXT NOT NULL,
                                schema_version TEXT NOT NULL,
                                title TEXT NOT NULL,
                                summary TEXT NOT NULL,
                                body TEXT NOT NULL,
                                status TEXT NOT NULL,
                                confidence REAL NOT NULL,
                                validation_state TEXT NOT NULL,
                                created_at TEXT NOT NULL,
                                updated_at TEXT NOT NULL,
                                created_by TEXT NOT NULL,
                                source_type TEXT NOT NULL,
                                security_classification TEXT NOT NULL,
                                evidence TEXT NOT NULL,
                                supersedes TEXT,
                                superseded_by TEXT,
                                why_created TEXT NOT NULL,
                                problem_solved TEXT NOT NULL,
                                future_work_dependent TEXT NOT NULL,
                                extra_metadata TEXT,
                                deleted INTEGER DEFAULT 0
                            );
                        """)
                        conn.execute("""
                            CREATE TABLE card_tags (
                                card_id TEXT NOT NULL,
                                tag TEXT NOT NULL,
                                PRIMARY KEY (card_id, tag),
                                FOREIGN KEY (card_id) REFERENCES cards(card_id) ON DELETE CASCADE
                            );
                        """)
                        conn.execute("""
                            CREATE TABLE card_links (
                                link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                source_id TEXT NOT NULL,
                                target_id TEXT NOT NULL,
                                link_type TEXT NOT NULL,
                                UNIQUE (source_id, target_id, link_type)
                            );
                        """)
                        conn.execute("""
                            CREATE TABLE card_sources (
                                card_id TEXT NOT NULL,
                                source_id TEXT NOT NULL,
                                PRIMARY KEY (card_id, source_id),
                                FOREIGN KEY (card_id) REFERENCES cards(card_id) ON DELETE CASCADE
                            );
                        """)
                        conn.execute("""
                            CREATE TABLE card_revisions (
                                revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                card_id TEXT NOT NULL,
                                revision_number INTEGER NOT NULL,
                                serialized_card TEXT NOT NULL,
                                updated_at TEXT NOT NULL,
                                updated_by TEXT NOT NULL,
                                reason TEXT,
                                FOREIGN KEY (card_id) REFERENCES cards(card_id) ON DELETE CASCADE
                            );
                        """)
                        conn.execute(
                            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                            (1, datetime.datetime.now(datetime.UTC).isoformat())
                        )

                # Re-query current version to apply sequential migrations
                cursor.execute("SELECT MAX(version) FROM schema_version")
                current_version = cursor.fetchone()[0]

                # Migration 2: Add optional embedding column
                if current_version < 2:
                    with conn:
                        conn.execute("ALTER TABLE cards ADD COLUMN embedding TEXT;")
                        conn.execute(
                            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                            (2, datetime.datetime.now(datetime.UTC).isoformat())
                        )

            finally:
                conn.close()

    def store_card(self, card: KnowledgeCard, updater: str = "system", reason: str | None = None) -> None:
        """Atomically inserts or updates a card and logs a revision."""
        # Validate first
        card.validate()

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")

                # Check if card exists
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM cards WHERE card_id = ?", (card.card_id,))
                exists = cursor.fetchone()[0] > 0

                # Extract embedding if present in extra_metadata
                embedding_list = card.extra_metadata.get("embedding")
                embedding_json = json.dumps(embedding_list) if embedding_list else None

                meta_json = json.dumps(card.extra_metadata)

                if not exists:
                    # Insert
                    conn.execute("""
                        INSERT INTO cards (
                            card_id, card_type, schema_version, title, summary, body, status,
                            confidence, validation_state, created_at, updated_at, created_by,
                            source_type, security_classification, evidence, supersedes, superseded_by,
                            why_created, problem_solved, future_work_dependent, extra_metadata, deleted, embedding
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                    """, (
                        card.card_id, card.card_type, card.schema_version, card.title, card.summary,
                        card.body, card.status, card.confidence, card.validation_state, card.created_at,
                        card.updated_at, card.created_by, card.source_type, card.security_classification,
                        card.evidence, card.supersedes, card.superseded_by, card.why_created,
                        card.problem_solved, card.future_work_dependent, meta_json, embedding_json
                    ))
                    revision_num = 1
                else:
                    # Update
                    conn.execute("""
                        UPDATE cards SET
                            card_type = ?, schema_version = ?, title = ?, summary = ?, body = ?, status = ?,
                            confidence = ?, validation_state = ?, updated_at = ?, source_type = ?,
                            security_classification = ?, evidence = ?, supersedes = ?, superseded_by = ?,
                            why_created = ?, problem_solved = ?, future_work_dependent = ?, extra_metadata = ?,
                            embedding = ?
                        WHERE card_id = ? AND deleted = 0
                    """, (
                        card.card_type, card.schema_version, card.title, card.summary, card.body, card.status,
                        card.confidence, card.validation_state, card.updated_at, card.source_type,
                        card.security_classification, card.evidence, card.supersedes, card.superseded_by,
                        card.why_created, card.problem_solved, card.future_work_dependent, meta_json,
                        embedding_json, card.card_id
                    ))
                    # Get next revision number
                    cursor.execute("SELECT COALESCE(MAX(revision_number), 0) FROM card_revisions WHERE card_id = ?", (card.card_id,))
                    revision_num = cursor.fetchone()[0] + 1

                # Manage tags
                conn.execute("DELETE FROM card_tags WHERE card_id = ?", (card.card_id,))
                for tag in card.tags:
                    conn.execute("INSERT OR IGNORE INTO card_tags (card_id, tag) VALUES (?, ?)", (card.card_id, tag))

                # Manage source_ids
                conn.execute("DELETE FROM card_sources WHERE card_id = ?", (card.card_id,))
                for s_id in card.source_ids:
                    conn.execute("INSERT OR IGNORE INTO card_sources (card_id, source_id) VALUES (?, ?)", (card.card_id, s_id))

                # Manage card links
                conn.execute("DELETE FROM card_links WHERE source_id = ? AND link_type IN ('PARENT', 'RELATED')", (card.card_id,))
                for p_id in card.parent_card_ids:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'PARENT')", (card.card_id, p_id))
                for r_id in card.related_card_ids:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'RELATED')", (card.card_id, r_id))
                if card.supersedes:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'SUPERSEDES')", (card.card_id, card.supersedes))

                # Write full revision log
                serialized = json.dumps(card.to_dict())
                conn.execute("""
                    INSERT INTO card_revisions (card_id, revision_number, serialized_card, updated_at, updated_by, reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (card.card_id, revision_num, serialized, card.updated_at, updater, reason))

                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def get_card(self, card_id: str, include_deleted: bool = False) -> KnowledgeCard | None:
        """Retrieves a card by ID."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                query = "SELECT * FROM cards WHERE card_id = ?"
                if not include_deleted:
                    query += " AND deleted = 0"
                cursor.execute(query, (card_id,))
                row = cursor.fetchone()
                if not row:
                    return None

                card_data = dict(row)

                # Fetch tags
                cursor.execute("SELECT tag FROM card_tags WHERE card_id = ?", (card_id,))
                card_data["tags"] = [r[0] for r in cursor.fetchall()]

                # Fetch source IDs
                cursor.execute("SELECT source_id FROM card_sources WHERE card_id = ?", (card_id,))
                card_data["source_ids"] = [r[0] for r in cursor.fetchall()]

                # Fetch parent card IDs
                cursor.execute("SELECT target_id FROM card_links WHERE source_id = ? AND link_type = 'PARENT'", (card_id,))
                card_data["parent_card_ids"] = [r[0] for r in cursor.fetchall()]

                # Fetch related card IDs
                cursor.execute("SELECT target_id FROM card_links WHERE source_id = ? AND link_type = 'RELATED'", (card_id,))
                card_data["related_card_ids"] = [r[0] for r in cursor.fetchall()]

                card_data["extra_metadata"] = json.loads(card_data["extra_metadata"]) if card_data.get("extra_metadata") else {}

                # Retrieve embedding column if present and populate in extra_metadata
                if card_data.get("embedding"):
                    card_data["extra_metadata"]["embedding"] = json.loads(card_data["embedding"])

                return KnowledgeCard.from_dict(card_data)
            finally:
                conn.close()

    def get_revision_history(self, card_id: str) -> list[dict[str, Any]]:
        """Returns the complete list of revisions for a given card."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT revision_number, serialized_card, updated_at, updated_by, reason
                    FROM card_revisions WHERE card_id = ? ORDER BY revision_number ASC
                """, (card_id,))
                revisions = []
                for r in cursor.fetchall():
                    revisions.append({
                        "revision_number": r["revision_number"],
                        "serialized_card": json.loads(r["serialized_card"]),
                        "updated_at": r["updated_at"],
                        "updated_by": r["updated_by"],
                        "reason": r["reason"]
                    })
                return revisions
            finally:
                conn.close()

    def soft_delete_card(self, card_id: str, updater: str = "system", reason: str | None = None) -> bool:
        """Soft deletes (deprecates/marks as deleted) a card."""
        with self._lock:
            card = self.get_card(card_id)
            if not card:
                return False

            card.status = "DEPRECATED"
            card.updated_at = datetime.datetime.now(datetime.UTC).isoformat()

            conn = self._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                conn.execute("UPDATE cards SET deleted = 1, status = 'DEPRECATED', updated_at = ? WHERE card_id = ?", (card.updated_at, card_id))

                # Write revision
                serialized = json.dumps(card.to_dict())
                cursor = conn.cursor()
                cursor.execute("SELECT COALESCE(MAX(revision_number), 0) FROM card_revisions WHERE card_id = ?", (card_id,))
                revision_num = cursor.fetchone()[0] + 1

                conn.execute("""
                    INSERT INTO card_revisions (card_id, revision_number, serialized_card, updated_at, updated_by, reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (card_id, revision_num, serialized, card.updated_at, updater, reason or "Soft Deleted / Deprecated"))

                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def list_all_cards(self, include_deleted: bool = False) -> list[KnowledgeCard]:
        """Returns all non-deleted cards."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                query = "SELECT card_id FROM cards"
                if not include_deleted:
                    query += " WHERE deleted = 0"
                cursor.execute(query)
                card_ids = [row[0] for row in cursor.fetchall()]
            finally:
                conn.close()

            cards = []
            for cid in card_ids:
                card = self.get_card(cid, include_deleted)
                if card:
                    cards.append(card)
            return cards

    def export_to_jsonl(self, filepath: str) -> None:
        """Exports all cards in the database to a JSONL file."""
        with self._lock:
            cards = self.list_all_cards(include_deleted=True)
            with open(filepath, "w") as f:
                for card in cards:
                    serialized = card.to_dict()
                    # Include a 'deleted' flag in the export so it can be restored exactly
                    conn = self._get_connection()
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT deleted FROM cards WHERE card_id = ?", (card.card_id,))
                        row = cursor.fetchone()
                        serialized["_deleted"] = row[0] if row else 0
                    finally:
                        conn.close()
                    f.write(json.dumps(serialized) + "\n")

    def import_from_jsonl(self, filepath: str, updater: str = "importer") -> None:
        """Imports cards from a JSONL file, preserving history/status or soft delete flags."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"JSONL import file not found: {filepath}")

        with self._lock:
            with open(filepath, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    deleted = data.pop("_deleted", 0)
                    card = KnowledgeCard.from_dict(data)

                    # Check if it should be restored/updated
                    self.store_card(card, updater=updater, reason="Imported from JSONL")
                    if deleted:
                        self.soft_delete_card(card.card_id, updater=updater, reason="Imported as soft-deleted")
