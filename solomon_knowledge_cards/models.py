import os
import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    """Manages the SQLite database connection, initialization, and safe migrations."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure parent directories exist
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        conn = self.get_connection()
        try:
            with conn:
                # Create migrations table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS migrations (
                        version INTEGER PRIMARY KEY
                    );
                """)
                # Get current migration version
                cursor = conn.execute("SELECT MAX(version) as max_v FROM migrations")
                row = cursor.fetchone()
                current_v = row["max_v"] if row and row["max_v"] is not None else 0

                # Migration 1: Knowledge Cards, Revisions, Worker Reports, Reviews
                if current_v < 1:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS knowledge_cards (
                            card_id TEXT PRIMARY KEY,
                            card_type TEXT NOT NULL,
                            title TEXT NOT NULL,
                            summary TEXT NOT NULL,
                            body TEXT NOT NULL,
                            confidence REAL DEFAULT 0.0,
                            validation_state TEXT NOT NULL DEFAULT 'DRAFT',
                            security_classification TEXT NOT NULL DEFAULT 'INTERNAL',
                            source_ids TEXT NOT NULL, -- JSON array of strings
                            created_at TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS revisions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            card_id TEXT NOT NULL,
                            version INTEGER NOT NULL,
                            title TEXT NOT NULL,
                            summary TEXT NOT NULL,
                            body TEXT NOT NULL,
                            confidence REAL DEFAULT 0.0,
                            validation_state TEXT NOT NULL,
                            security_classification TEXT NOT NULL,
                            modifier TEXT NOT NULL,
                            reason TEXT,
                            created_at TEXT NOT NULL
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS worker_reports (
                            report_id TEXT PRIMARY KEY,
                            task_id TEXT NOT NULL,
                            procedure_ids TEXT NOT NULL, -- JSON array of strings
                            worker_id TEXT NOT NULL,
                            worker_type TEXT NOT NULL,
                            started_at TEXT NOT NULL,
                            completed_at TEXT NOT NULL,
                            outcome TEXT NOT NULL,
                            attempted TEXT NOT NULL,
                            succeeded TEXT NOT NULL,
                            failed TEXT NOT NULL,
                            root_cause TEXT,
                            repair_action TEXT,
                            evidence TEXT NOT NULL, -- JSON array of objects
                            changed_files TEXT NOT NULL, -- JSON array of strings
                            test_results TEXT NOT NULL, -- JSON string
                            security_classification TEXT NOT NULL DEFAULT 'INTERNAL',
                            candidate_learning INTEGER DEFAULT 1,
                            created_at TEXT NOT NULL
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS reviews (
                            review_id TEXT PRIMARY KEY,
                            card_id TEXT NOT NULL,
                            reviewer TEXT NOT NULL,
                            decision TEXT NOT NULL,
                            notes TEXT,
                            reason TEXT,
                            evidence_checked INTEGER DEFAULT 0,
                            confidence REAL DEFAULT 0.0,
                            timestamp TEXT NOT NULL
                        );
                    """)
                    # Create indexes
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_state ON knowledge_cards(validation_state);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_cards_classification ON knowledge_cards(security_classification);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_revisions_card ON revisions(card_id);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_card ON reviews(card_id);")

                    conn.execute("INSERT INTO migrations (version) VALUES (1);")
        finally:
            conn.close()
