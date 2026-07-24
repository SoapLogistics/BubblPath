import logging
import sqlite3
import json
import threading

class SolomonCognitiveArchitecture:
    """
    Implements the foundational data structures and logic for the Artificial Cognitive Architecture.
    Includes:
    1. Perpetual Learning Engine (Learning Events)
    2. Knowledge Graph & Relational Intelligence (Nodes and Edges)
    3. Autonomous Growth Loop (Experiments)
    4. Meta-Learning (Metrics)
    """
    def __init__(self, db_path="cognitive_architecture.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self._local = threading.local()
        self._initialize_db()

    def _get_connection(self):
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
        conn = self._get_connection()
        cursor = conn.cursor()

        # Campaign I: Perpetual Learning Engine
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
                usage_count INTEGER DEFAULT 0,
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Campaign II: Knowledge Graph
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                properties TEXT,
                last_accessed DATETIME,
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

        # Campaign III: Autonomous Growth Loop
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

        # Campaign IV: Meta-Learning
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


    # --- Campaign I: Perpetual Learning ---
    def record_learning_event(self, content, source="unknown", confidence=0.5,
                              source_reliability=0.5, reason_accepted=None, is_procedure=False):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO learning_events
               (content, source, confidence, source_reliability, reason_accepted, is_procedure)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (content, source, confidence, source_reliability, reason_accepted, is_procedure)
        )
        conn.commit()
        return cursor.lastrowid

    def get_learning_events(self, limit=10):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_events ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def extract_procedures(self):
        """Phase 4: Convert repeated workflows into procedures."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Super simple mock heuristic: look for learning events with words like "run", "install", "deploy"
        # and turn them into procedures.
        cursor.execute("SELECT * FROM learning_events WHERE is_procedure = 0 AND (content LIKE '%run %' OR content LIKE '%install %' OR content LIKE '%deploy %')")
        events = cursor.fetchall()

        extracted = 0
        for event in events:
            # Create a procedure
            cursor.execute(
                "INSERT INTO procedures (name, steps, quality_score) VALUES (?, ?, ?)",
                (f"Procedure derived from event {event['id']}", event['content'], 0.5)
            )
            # Mark event as procedure
            cursor.execute("UPDATE learning_events SET is_procedure = 1 WHERE id = ?", (event['id'],))
            extracted += 1

        conn.commit()
        return extracted


    # --- Campaign II: Knowledge Graph ---
    def add_graph_node(self, node_id, node_type, properties=None, cluster_id=None):
        if properties is None:
            properties = {}
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO graph_nodes (id, type, properties, cluster_id) VALUES (?, ?, ?, ?)",
            (node_id, node_type, json.dumps(properties), cluster_id)
        )
        conn.commit()
        return node_id

    def add_graph_edge(self, source_id, target_id, relationship, weight=1.0,
                       confidence=1.0, temporal_start=None, temporal_end=None, source_attribution=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO graph_edges
               (source_id, target_id, relationship, weight, confidence, temporal_start, temporal_end, source_attribution)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (source_id, target_id, relationship, weight, confidence, temporal_start, temporal_end, source_attribution)
        )
        conn.commit()
        return cursor.lastrowid

    def get_graph(self):
         conn = self._get_connection()
         cursor = conn.cursor()
         cursor.execute("SELECT * FROM graph_nodes")
         nodes = []
         for row in cursor.fetchall():
             n = dict(row)
             if n.get('properties'):
                 try:
                     n['properties'] = json.loads(n['properties'])
                 except json.JSONDecodeError:
                     pass
             nodes.append(n)

         cursor.execute("SELECT * FROM graph_edges")
         edges = [dict(row) for row in cursor.fetchall()]

         return {"nodes": nodes, "edges": edges}

    def semantic_link_nodes(self):
         """Knowledge Graph: Detect semantic similarity and create edges."""
         conn = self._get_connection()
         cursor = conn.cursor()

         # Mock implementation: randomly link disconnected nodes that share similar type
         cursor.execute("SELECT * FROM graph_nodes")
         nodes = cursor.fetchall()

         new_edges = 0
         for i in range(len(nodes)):
             for j in range(i + 1, len(nodes)):
                 n1 = nodes[i]
                 n2 = nodes[j]
                 if n1['type'] == n2['type']:
                     # Check if edge already exists
                     cursor.execute("SELECT id FROM graph_edges WHERE source_id = ? AND target_id = ?", (n1['id'], n2['id']))
                     if not cursor.fetchone():
                         self.add_graph_edge(n1['id'], n2['id'], "similar_type", 0.5)
                         new_edges += 1
         return new_edges


    # --- Campaign III: Autonomous Growth Loop ---
    def log_experiment(self, name, baseline_metric=None, experiment_metric=None, status="pending", result=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO experiments
               (name, baseline_metric, experiment_metric, status, result)
               VALUES (?, ?, ?, ?, ?)""",
            (name, baseline_metric, experiment_metric, status, result)
        )
        conn.commit()
        return cursor.lastrowid

    def add_research_goal(self, topic, expected_value=0.0, priority=1):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO research_goals (topic, expected_value, priority) VALUES (?, ?, ?)",
            (topic, expected_value, priority)
        )
        conn.commit()
        return cursor.lastrowid

    def add_daily_question(self, question):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO daily_questions (question) VALUES (?)",
            (question,)
        )
        conn.commit()
        return cursor.lastrowid


    # --- Campaign IV: Meta-Learning ---
    def log_meta_metric(self, metric_name, metric_value, context=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO meta_learning_metrics (metric_name, metric_value, context) VALUES (?, ?, ?)",
            (metric_name, metric_value, context)
        )
        conn.commit()
        return cursor.lastrowid

    def get_meta_metrics(self, limit=10):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM meta_learning_metrics ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def log_tool_effectiveness(self, tool_name, category, success_rate):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tool_effectiveness
               (tool_name, category, success_rate, usage_count)
               VALUES (?, ?, ?, 1)
               ON CONFLICT(tool_name) DO UPDATE SET
               success_rate = (tool_effectiveness.success_rate * tool_effectiveness.usage_count + ?) / (tool_effectiveness.usage_count + 1),
               usage_count = tool_effectiveness.usage_count + 1""",
            (tool_name, category, success_rate, success_rate)
        )
        conn.commit()
        return cursor.lastrowid
