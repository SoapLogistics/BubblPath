import sqlite3
import threading
import json
import logging

class SolomonDBManager:
    """Centralized DB manager for the Cognitive Architecture."""
    def __init__(self, db_path="cognitive_architecture.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self._local = threading.local()
        self._initialize_db()

    def get_connection(self):
        if self.db_path == ":memory:":
            if not hasattr(self, "_mem_conn"):
                self._mem_conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self._mem_conn.row_factory = sqlite3.Row
            return self._mem_conn

        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _initialize_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # --- Campaign I: Perpetual Learning ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT,
                confidence REAL,
                source_reliability REAL DEFAULT 0.5,
                reason_accepted TEXT,
                reason_rejected TEXT,
                version INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active', -- active, archived, conflicting
                is_procedure BOOLEAN DEFAULT 0,
                is_fact BOOLEAN DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                steps TEXT,
                quality_score REAL,
                version INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedure_rollbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                procedure_id INTEGER,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id_1 INTEGER,
                event_id_2 INTEGER,
                status TEXT DEFAULT 'pending_review',
                resolution TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # --- Campaign II: Knowledge Graph ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                properties TEXT,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                cluster_id TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relationship TEXT,
                weight REAL,
                confidence REAL DEFAULT 1.0,
                temporal_start DATETIME,
                temporal_end DATETIME,
                source_attribution TEXT,
                FOREIGN KEY(source_id) REFERENCES graph_nodes(id),
                FOREIGN KEY(target_id) REFERENCES graph_nodes(id)
            )
        ''')

        # --- Campaign III: Autonomous Growth Loop ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                baseline_metric REAL,
                experiment_metric REAL,
                status TEXT,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                expected_value REAL,
                priority INTEGER,
                status TEXT DEFAULT 'pending',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                status TEXT DEFAULT 'unanswered',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                observation_type TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # --- Campaign IV: Meta-Learning ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_learning_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT UNIQUE NOT NULL,
                category TEXT,
                success_rate REAL,
                usage_count INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
