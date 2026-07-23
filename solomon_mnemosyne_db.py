"""
Solomon Perpetual Learning Machine
Mnemosyne Relational SQLite Database & Hashing Embedder

This module manages the persistent storage of SOK cognitive cards,
computes deterministic 128-dimensional local fallback embeddings,
calculates cosine similarity searches with full division-by-zero protection,
and manages card confidence reinforcement scaling.
Now enhanced with:
- Thread-safe RLock concurrency control.
- SQL query execution speed tracking.
- Status column tracking & Revisions logging.
- Worker modes persistent configuration table.
"""

import sqlite3
import json
import math
import hashlib
import threading
import time
from typing import List, Dict, Any, Tuple

class SolomonMnemosyneDB:
    """
    Manages SQLite storage, hybrid semantic retrieval, confidence scaling,
    revisions logging, and worker modes with full thread-safe locking.
    """

    def __init__(self, db_path: str = "solomon_mnemosyne_demo.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self.query_latencies = []  # List of query execution times in ms (last 100)
        self._init_db()

    def _init_db(self):
        """
        Creates the SQLite tables if they do not exist.
        Includes a dynamic migration mechanism to add columns safely.
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 1. Create knowledge_cards table (including embedding and confidence)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_cards (
                    card_id TEXT PRIMARY KEY,
                    family TEXT NOT NULL,
                    focus TEXT,
                    content TEXT NOT NULL,
                    embedding TEXT,
                    confidence REAL DEFAULT 1.0,
                    status TEXT DEFAULT 'DRAFT'
                )
            """)

            # Dynamic Migration check: Add confidence if missing in pre-existing DB
            cursor.execute("PRAGMA table_info(knowledge_cards)")
            columns = [info[1] for info in cursor.fetchall()]
            if "confidence" not in columns:
                cursor.execute("ALTER TABLE knowledge_cards ADD COLUMN confidence REAL DEFAULT 1.0")
            if "status" not in columns:
                cursor.execute("ALTER TABLE knowledge_cards ADD COLUMN status TEXT DEFAULT 'DRAFT'")

            # 2. Create card_links table supporting relational directed links
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS card_links (
                    source_id TEXT,
                    target_id TEXT,
                    relationship_type TEXT,
                    PRIMARY KEY (source_id, target_id, relationship_type),
                    FOREIGN KEY (source_id) REFERENCES knowledge_cards (card_id) ON DELETE CASCADE,
                    FOREIGN KEY (target_id) REFERENCES knowledge_cards (card_id) ON DELETE CASCADE
                )
            """)

            # 3. Create revisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revisions (
                    revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (card_id) REFERENCES knowledge_cards (card_id) ON DELETE CASCADE
                )
            """)

            # 4. Create worker_modes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS worker_modes (
                    worker_name TEXT PRIMARY KEY,
                    execution_mode TEXT NOT NULL
                )
            """)

            # Seed default worker modes if empty
            cursor.execute("SELECT COUNT(*) FROM worker_modes")
            if cursor.fetchone()[0] == 0:
                default_modes = [
                    ("Gabriel", "READ_ONLY"),
                    ("Mnemosyne", "READ_ONLY"),
                    ("Prometheus", "DRY_RUN_ONLY"),
                    ("Loki", "RESEARCH_ONLY")
                ]
                cursor.executemany("INSERT INTO worker_modes (worker_name, execution_mode) VALUES (?, ?)", default_modes)

            conn.commit()
            conn.close()

            latency = (time.perf_counter() - start_time) * 1000.0
            self._record_latency(latency)

    def _record_latency(self, latency_ms: float):
        self.query_latencies.append(latency_ms)
        if len(self.query_latencies) > 100:
            self.query_latencies.pop(0)

    def get_average_query_latency_ms(self) -> float:
        """
        Returns the running average query response speed in milliseconds.
        """
        with self.lock:
            if not self.query_latencies:
                return 0.0
            return sum(self.query_latencies) / len(self.query_latencies)

    @classmethod
    def compute_local_embedding(cls, text: str) -> List[float]:
        """
        Computes a deterministic 128-dimensional local fallback hashing embedding.
        Splits text, hashes terms, populates 128 dimensions, and applies L2 normalization.
        """
        dimensions = 128
        vector = [0.0] * dimensions

        # Simple text processing
        words = text.lower().replace(",", " ").replace(".", " ").split()
        if not words:
            # Fallback for empty text
            vector[0] = 1.0
            return vector

        for word in words:
            # Generate deterministic hashes for each word
            h = hashlib.sha256(word.encode("utf-8")).hexdigest()
            # Generate multiple index activations per word for richness
            for i in range(3):
                part = h[i*8:(i+1)*8]
                if part:
                    idx = int(part, 16) % dimensions
                    # Activations decay or accumulate based on word hashing
                    val = (int(h[(i+1)*8:(i+2)*8], 16) % 100) / 100.0 if idx < dimensions - 1 else 0.5
                    vector[idx] += val

        # L2 Normalization
        sq_sum = sum(x ** 2 for x in vector)
        norm = math.sqrt(sq_sum)

        # Division by zero protection
        if norm < 1e-9:
            vector[0] = 1.0
            return vector

        return [float(x / norm) for x in vector]

    def upsert_card(self, card_id: str, family: str, focus: str, content: str, status: str = 'DRAFT') -> bool:
        """
        Upserts a SOK card, automatically calculating and caching its local vector embedding.
        Preserves existing confidence scores on update if already on disk.
        """
        with self.lock:
            start_time = time.perf_counter()
            embedding_vector = self.compute_local_embedding(content)
            embedding_json = json.dumps(embedding_vector)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            try:
                # Check if card already exists to preserve confidence & status
                cursor.execute("SELECT confidence, status FROM knowledge_cards WHERE card_id = ?", (card_id,))
                row = cursor.fetchone()
                if row:
                    confidence = row[0]
                    # Only overwrite status if explicitly passed non-default or card is new
                    current_status = status if status != 'DRAFT' else row[1]
                else:
                    confidence = 1.0
                    current_status = status

                cursor.execute("""
                    INSERT INTO knowledge_cards (card_id, family, focus, content, embedding, confidence, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(card_id) DO UPDATE SET
                        family=excluded.family,
                        focus=excluded.focus,
                        content=excluded.content,
                        embedding=excluded.embedding,
                        status=CASE WHEN excluded.status != 'DRAFT' THEN excluded.status ELSE knowledge_cards.status END
                """, (card_id, family, focus, content, embedding_json, confidence, current_status))
                conn.commit()
                return True
            except sqlite3.Error:
                return False
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)

    def update_card_status(self, card_id: str, status: str, content: str = None) -> bool:
        """
        Updates the status of a SOK card in knowledge_cards and logs a new revision in the revisions table.
        If content is provided, updates the card content as well.
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                # Check if card exists
                cursor.execute("SELECT content FROM knowledge_cards WHERE card_id = ?", (card_id,))
                row = cursor.fetchone()
                if not row:
                    return False

                current_content = content if content is not None else row[0]

                # Compute embedding for content
                embedding_vector = self.compute_local_embedding(current_content)
                embedding_json = json.dumps(embedding_vector)

                if content is not None:
                    cursor.execute("""
                        UPDATE knowledge_cards
                        SET status = ?, content = ?, embedding = ?
                        WHERE card_id = ?
                    """, (status, current_content, embedding_json, card_id))
                else:
                    cursor.execute("""
                        UPDATE knowledge_cards
                        SET status = ?
                        WHERE card_id = ?
                    """, (status, card_id))

                # Log to revisions
                cursor.execute("""
                    INSERT INTO revisions (card_id, status, content, embedding)
                    VALUES (?, ?, ?, ?)
                """, (card_id, status, current_content, embedding_json))

                conn.commit()
                return True
            except sqlite3.Error:
                return False
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)

    def get_revisions(self, card_id: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves all revisions, optionally filtered by card_id.
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            revisions = []
            try:
                if card_id:
                    cursor.execute("SELECT * FROM revisions WHERE card_id = ? ORDER BY timestamp DESC", (card_id,))
                else:
                    cursor.execute("SELECT * FROM revisions ORDER BY timestamp DESC")
                for row in cursor.fetchall():
                    rev = dict(row)
                    if rev["embedding"]:
                        rev["embedding"] = json.loads(rev["embedding"])
                    revisions.append(rev)
            except sqlite3.Error:
                pass
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)
            return revisions

    def get_worker_modes(self) -> Dict[str, str]:
        """
        Retrieves all worker execution modes from SQLite.
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            modes = {}
            try:
                cursor.execute("SELECT worker_name, execution_mode FROM worker_modes")
                for row in cursor.fetchall():
                    modes[row[0]] = row[1]
            except sqlite3.Error:
                pass
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)
            return modes

    def update_worker_mode(self, worker_name: str, execution_mode: str) -> bool:
        """
        Updates or inserts an execution mode for a helper worker.
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO worker_modes (worker_name, execution_mode)
                    VALUES (?, ?)
                    ON CONFLICT(worker_name) DO UPDATE SET execution_mode=excluded.execution_mode
                """, (worker_name, execution_mode))
                conn.commit()
                return True
            except sqlite3.Error:
                return False
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)

    def update_card_confidence(self, card_id: str, outcome: str, learning_rate: float = 0.05) -> Tuple[bool, float]:
        """
        Dynamically scales the confidence score of a SOK card based on success/failure outcomes.
        Clips score strictly inside the stable boundary of [0.1, 2.0].
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT confidence FROM knowledge_cards WHERE card_id = ?", (card_id,))
                row = cursor.fetchone()
                if not row:
                    return False, 1.0

                old_confidence = row[0]

                # Apply reinforcement factor
                if outcome == "success":
                    new_confidence = old_confidence * (1.0 + learning_rate)
                elif outcome == "failure":
                    new_confidence = old_confidence * (1.0 - learning_rate)
                else:
                    new_confidence = old_confidence

                # Enforce strict confidence boundaries [0.1, 2.0]
                new_confidence = max(0.1, min(2.0, new_confidence))

                cursor.execute("""
                    UPDATE knowledge_cards SET confidence = ?
                    WHERE card_id = ?
                """, (new_confidence, card_id))
                conn.commit()
                return True, float(round(new_confidence, 4))
            except sqlite3.Error:
                return False, 1.0
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)

    def add_link(self, source_id: str, target_id: str, relationship_type: str) -> bool:
        """
        Creates a directed link between SOK cards (e.g. DEPENDS_ON, ENHANCES).
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO card_links (source_id, target_id, relationship_type)
                    VALUES (?, ?, ?)
                    ON CONFLICT DO NOTHING
                """, (source_id, target_id, relationship_type))
                conn.commit()
                return True
            except sqlite3.Error:
                return False
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)

    def get_card(self, card_id: str) -> Dict[str, Any]:
        """
        Retrieves a single card with its direct link metadata and confidence score.
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            card = None
            try:
                cursor.execute("SELECT * FROM knowledge_cards WHERE card_id = ?", (card_id,))
                row = cursor.fetchone()
                if row:
                    card = dict(row)
                    if card["embedding"]:
                        card["embedding"] = json.loads(card["embedding"])

                    # Fetch outgoing relationships
                    cursor.execute("""
                        SELECT target_id, relationship_type FROM card_links
                        WHERE source_id = ?
                    """, (card_id,))
                    card["outgoing_links"] = [dict(r) for r in cursor.fetchall()]

                    # Fetch incoming relationships
                    cursor.execute("""
                        SELECT source_id, relationship_type FROM card_links
                        WHERE target_id = ?
                    """, (card_id,))
                    card["incoming_links"] = [dict(r) for r in cursor.fetchall()]
            except sqlite3.Error:
                pass
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)
            return card

    def get_all_cards(self) -> List[Dict[str, Any]]:
        """
        Retrieves all SOK cards stored in the database.
        """
        with self.lock:
            start_time = time.perf_counter()
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cards = []
            try:
                cursor.execute("SELECT * FROM knowledge_cards")
                for row in cursor.fetchall():
                    card = dict(row)
                    if card["embedding"]:
                        card["embedding"] = json.loads(card["embedding"])
                    cards.append(card)
            except sqlite3.Error:
                pass
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)
            return cards

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a cosine similarity search against cached embeddings.
        Includes division-by-zero protection and caps similarity score to [-1.0, 1.0].
        """
        with self.lock:
            start_time = time.perf_counter()
            query_vector = self.compute_local_embedding(query)

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            results = []
            try:
                cursor.execute("SELECT card_id, family, focus, content, embedding, confidence, status FROM knowledge_cards")
                for row in cursor.fetchall():
                    card = dict(row)
                    if not card["embedding"]:
                        continue

                    card_vector = json.loads(card["embedding"])

                    # Compute Cosine Similarity
                    dot_product = sum(q * c for q, c in zip(query_vector, card_vector))

                    query_norm = math.sqrt(sum(q ** 2 for q in query_vector))
                    card_norm = math.sqrt(sum(c ** 2 for c in card_vector))

                    denom = query_norm * card_norm
                    if denom < 1e-9:
                        similarity = 0.0
                    else:
                        similarity = dot_product / denom

                    similarity = max(-1.0, min(1.0, similarity))

                    results.append({
                        "card_id": card["card_id"],
                        "family": card["family"],
                        "focus": card["focus"],
                        "content": card["content"],
                        "confidence": card["confidence"],
                        "status": card.get("status", "DRAFT"),
                        "similarity": round(float(similarity), 4)
                    })
            except sqlite3.Error:
                pass
            finally:
                conn.close()
                self._record_latency((time.perf_counter() - start_time) * 1000.0)

            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
