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

                # Migration 2: Relational links table & execution_traces for debugging
                if current_v < 2:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS card_links (
                            source_id TEXT NOT NULL,
                            target_id TEXT NOT NULL,
                            relationship_type TEXT NOT NULL, -- DEPENDS_ON, PREVENTS, ENHANCES, PROPOSES_UPDATE_TO
                            created_at TEXT NOT NULL,
                            PRIMARY KEY (source_id, target_id, relationship_type),
                            FOREIGN KEY (source_id) REFERENCES knowledge_cards(card_id) ON DELETE CASCADE,
                            FOREIGN KEY (target_id) REFERENCES knowledge_cards(card_id) ON DELETE CASCADE
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS execution_traces (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            request_id TEXT NOT NULL,
                            conversation_id TEXT NOT NULL,
                            step_name TEXT NOT NULL,
                            details TEXT NOT NULL, -- JSON formatted details or plain-text
                            timestamp TEXT NOT NULL
                        );
                    """)
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_traces_request ON execution_traces(request_id);")
                    conn.execute("INSERT INTO migrations (version) VALUES (2);")

                # Migration 3: Adding embedding column to knowledge_cards and revisions table
                if current_v < 3:
                    # check if column already exists to prevent error if run twice
                    cursor = conn.execute("PRAGMA table_info(knowledge_cards);")
                    columns = [col["name"] for col in cursor.fetchall()]
                    if "embedding" not in columns:
                        conn.execute("ALTER TABLE knowledge_cards ADD COLUMN embedding TEXT;")

                    cursor_rev = conn.execute("PRAGMA table_info(revisions);")
                    columns_rev = [col["name"] for col in cursor_rev.fetchall()]
                    if "embedding" not in columns_rev:
                        conn.execute("ALTER TABLE revisions ADD COLUMN embedding TEXT;")

                    conn.execute("INSERT INTO migrations (version) VALUES (3);")

                # Migration 4: Adding worker_modes table
                if current_v < 4:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS worker_modes (
                            worker_id TEXT PRIMARY KEY,
                            worker_name TEXT NOT NULL,
                            role TEXT NOT NULL,
                            mode TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        );
                    """)
                    now_str = datetime.utcnow().isoformat()
                    conn.execute("""
                        INSERT OR IGNORE INTO worker_modes (worker_id, worker_name, role, mode, updated_at)
                        VALUES
                        ('gabriel', 'Gabriel', 'COMMAND_CENTER_RELAY', 'READ_ONLY', ?),
                        ('mnemosyne', 'Mnemosyne', 'MEMORY_CONTEXT', 'READ_ONLY', ?),
                        ('prometheus', 'Prometheus', 'BUILD_PLANNER', 'DRY_RUN_ONLY', ?),
                        ('loki', 'Loki', 'SPORTS_RESEARCH_MODEL', 'RESEARCH_ONLY', ?);
                    """, (now_str, now_str, now_str, now_str))

                    conn.execute("INSERT INTO migrations (version) VALUES (4);")

                # Migration 5: Adding Loki bets and bankroll tables
                if current_v < 5:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_bets (
                            bet_id TEXT PRIMARY KEY,
                            sport TEXT NOT NULL,
                            fixture TEXT NOT NULL,
                            market TEXT NOT NULL,
                            outcome TEXT NOT NULL,
                            odds REAL NOT NULL,
                            shin_prob REAL NOT NULL,
                            kelly_fraction REAL NOT NULL,
                            stake REAL NOT NULL,
                            status TEXT NOT NULL, -- PENDING, WON, LOST
                            profit_loss REAL DEFAULT 0.0,
                            created_at TEXT NOT NULL,
                            resolved_at TEXT
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_bankroll (
                            bankroll_id TEXT PRIMARY KEY,
                            balance REAL NOT NULL,
                            updated_at TEXT NOT NULL
                        );
                    """)
                    now_str = datetime.utcnow().isoformat()
                    conn.execute("""
                        INSERT OR IGNORE INTO loki_bankroll (bankroll_id, balance, updated_at)
                        VALUES ('default', 10000.0, ?);
                    """, (now_str,))

                    conn.execute("INSERT INTO migrations (version) VALUES (5);")

                # Migration 6: Adding loki_learning_weights table
                if current_v < 6:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_learning_weights (
                            category_id TEXT PRIMARY KEY,
                            sport TEXT NOT NULL,
                            market TEXT NOT NULL,
                            total_bets INTEGER DEFAULT 0,
                            won_bets INTEGER DEFAULT 0,
                            confidence_modifier REAL DEFAULT 1.0,
                            updated_at TEXT NOT NULL
                        );
                    """)
                    conn.execute("INSERT INTO migrations (version) VALUES (6);")


                # Migration 7: Loki Advanced Data Structures
                if current_v < 7:
                    now_str = datetime.utcnow().isoformat()
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_equity_snapshots (
                            snapshot_id TEXT PRIMARY KEY,
                            bankroll REAL NOT NULL,
                            vault REAL NOT NULL,
                            timestamp TEXT NOT NULL
                        );
                    """)
                    conn.execute("INSERT OR IGNORE INTO loki_bankroll (bankroll_id, balance, updated_at) VALUES ('vault', 0.0, ?);", (now_str,))
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_advanced_learning (
                            category_id TEXT PRIMARY KEY,
                            sport TEXT NOT NULL,
                            market TEXT NOT NULL,
                            odds_band TEXT NOT NULL,
                            total_bets INTEGER DEFAULT 0,
                            won_bets INTEGER DEFAULT 0,
                            confidence_modifier REAL DEFAULT 1.0,
                            updated_at TEXT NOT NULL
                        );
                    """)
                    conn.execute("INSERT INTO migrations (version) VALUES (7);")


                # Migration 8: Loki Arbitrage, ML, Notifications, and Streaks
                if current_v < 8:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_ml_features (
                            bet_id TEXT PRIMARY KEY,
                            feature_json TEXT NOT NULL,
                            timestamp TEXT NOT NULL
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_notifications (
                            notification_id TEXT PRIMARY KEY,
                            type TEXT NOT NULL,
                            message TEXT NOT NULL,
                            is_read INTEGER DEFAULT 0,
                            created_at TEXT NOT NULL
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS loki_team_stats (
                            team_name TEXT PRIMARY KEY,
                            current_streak INTEGER DEFAULT 0,
                            updated_at TEXT NOT NULL
                        );
                    """)
                    conn.execute("INSERT INTO migrations (version) VALUES (8);")

        finally:



            conn.close()
