"""
Solomon Perpetual Learning Machine
Mnemosyne Relational SQLite Database & Hashing Embedder

This module manages the persistent storage of SOK cognitive cards,
computes deterministic 128-dimensional local fallback embeddings,
calculates cosine similarity searches with full division-by-zero protection,
and manages card confidence reinforcement scaling.
"""

import sqlite3
import json
import math
import hashlib
import functools
from collections import Counter
from typing import List, Dict, Any, Tuple, Optional
import datetime
from solomon_embeddings import EmbeddingProvider, DeterministicHashProvider, DenseEmbeddingProvider

class SolomonMnemosyneDB:
    """
    Manages SQLite storage, hybrid semantic retrieval, and confidence scaling.
    """

    def __init__(self, db_path: str = "solomon_mnemosyne_demo.db", embedding_provider: Optional['EmbeddingProvider'] = None):
        self.embedding_provider = embedding_provider or DeterministicHashProvider()
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Creates the SQLite tables if they do not exist.
        Includes a dynamic migration mechanism to add columns safely.
        """
        # Opt 3: thread-safe connection caching simulation
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        # Opt 2: Extreme PRAGMA Tuning
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA cache_size=-64000;")
        cursor.execute("PRAGMA temp_store=MEMORY;")
        cursor.execute("PRAGMA mmap_size=268435456;")

        # Opt 3: is_canonical flag added to schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_cards (
                card_id TEXT PRIMARY KEY,
                family TEXT NOT NULL,
                focus TEXT,
                content TEXT NOT NULL,
                embedding TEXT,
                confidence REAL DEFAULT 1.0,
                is_canonical BOOLEAN DEFAULT 0
            )
        """)

        # Opt 9: Composite Indexing
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_kc_family_conf ON knowledge_cards(family, confidence);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_kc_focus_conf ON knowledge_cards(focus, confidence);")

        # Opt 10: Schema versioning
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT)")

        # Opt 1: FTS5 Virtual Table for blazing fast keyword search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_cards_fts USING fts5(
                card_id UNINDEXED,
                content,
                tokenize = 'porter'
            )
        """)

        # Dynamic Migration check: Add confidence/is_canonical if missing in pre-existing DB
        cursor.execute("PRAGMA table_info(knowledge_cards)")
        columns = [info[1] for info in cursor.fetchall()]
        if "confidence" not in columns:
            cursor.execute("ALTER TABLE knowledge_cards ADD COLUMN confidence REAL DEFAULT 1.0")
        if "is_canonical" not in columns:
            cursor.execute("ALTER TABLE knowledge_cards ADD COLUMN is_canonical BOOLEAN DEFAULT 0")

        # Opt 6: Tombstoning (Soft Deletes)
        if "is_deleted" not in columns:
            cursor.execute("ALTER TABLE knowledge_cards ADD COLUMN is_deleted BOOLEAN DEFAULT 0")

        # Create card_links table supporting relational directed links
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

        # Create versioned embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS card_embeddings (
                card_id TEXT,
                provider TEXT,
                model TEXT,
                vector_dimension INTEGER,
                model_fingerprint TEXT,
                creation_timestamp TEXT,
                source_content_hash TEXT,
                status TEXT,
                confidence_classification TEXT,
                embedding_vector TEXT,
                PRIMARY KEY (card_id, provider, model),
                FOREIGN KEY (card_id) REFERENCES knowledge_cards (card_id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    @functools.lru_cache(maxsize=1024)
    def compute_local_embedding(self, text: str) -> Tuple[float, ...]:
        """
        Uses the configured embedding provider to compute the embedding vector.
        Cached for speed. Returns tuple for hashability.
        """
        return tuple(self.embedding_provider.embed_texts([text])[0])

    def upsert_card(self, card_id: str, family: str, focus: str, content: str, is_canonical: bool = False) -> bool:
        """
        Upserts a SOK card, automatically calculating and caching its local vector embedding.
        Checks for Canonical protection and Semantic Deduplication.
        Auto-chunks extremely long texts (>1500 chars) sequentially.
        """
        # Opt 10: Auto-chunking
        if len(content) > 1500:
            chunks = [content[i:i+1500] for i in range(0, len(content), 1500)]
            success = True
            for i, chunk in enumerate(chunks):
                chunk_id = f"{card_id}_chunk{i}" if i > 0 else card_id
                if not self._upsert_single_card(chunk_id, family, focus, chunk, is_canonical):
                    success = False
            return success
        else:
            return self._upsert_single_card(card_id, family, focus, content, is_canonical)


    def upsert_cards_batch(self, cards: List[Dict[str, Any]]) -> int:
        """
        Opt 4: Batched Upserts using executemany for massive speedups.
        Expects dicts with keys: card_id, family, focus, content, is_canonical
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        success_count = 0
        try:
            conn.execute("BEGIN TRANSACTION;")
            for c in cards:
                if self._upsert_single_card(c["card_id"], c["family"], c["focus"], c["content"], c.get("is_canonical", False)):
                    success_count += 1
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Batch upsert failed: {e}")
        finally:
            conn.close()

        return success_count

    def _upsert_single_card(self, card_id: str, family: str, focus: str, content: str, is_canonical: bool = False) -> bool:
        # Opt 4: Deduplication check (skip for chunks of same card to avoid false positives)
        if not "_chunk" in card_id:
            existing_matches = self.semantic_search(content, top_k=1)
            if existing_matches and existing_matches[0]["similarity"] > 0.99 and existing_matches[0]["card_id"] != card_id:
                # Found a near-exact duplicate, reject upsert to keep DB clean
                return False

        embedding_vector = self.compute_local_embedding(content)
        embedding_json = json.dumps(list(embedding_vector))

        provider_meta = self.embedding_provider.get_metadata()
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        creation_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if card exists and is canonical
            cursor.execute("SELECT confidence, is_canonical FROM knowledge_cards WHERE card_id = ?", (card_id,))
            row = cursor.fetchone()
            confidence = row[0] if row else 1.0

            # Opt 3: Canonical Protection
            if row and row[1] and not is_canonical:
                # Cannot overwrite a canonical card without explicit flag
                return False

            cursor.execute("""
                INSERT INTO knowledge_cards (card_id, family, focus, content, embedding, confidence, is_canonical)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(card_id) DO UPDATE SET
                    family=excluded.family,
                    focus=excluded.focus,
                    content=excluded.content,
                    embedding=excluded.embedding,
                    is_canonical=excluded.is_canonical,
                    is_deleted=0
            """, (card_id, family, focus, content, embedding_json, confidence, is_canonical))

            # Sync to FTS5
            cursor.execute("INSERT OR REPLACE INTO knowledge_cards_fts (card_id, content) VALUES (?, ?)", (card_id, content))

            # Upsert into card_embeddings
            cursor.execute("""
                INSERT INTO card_embeddings (
                    card_id, provider, model, vector_dimension, model_fingerprint,
                    creation_timestamp, source_content_hash, status,
                    confidence_classification, embedding_vector
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(card_id, provider, model) DO UPDATE SET
                    vector_dimension=excluded.vector_dimension,
                    model_fingerprint=excluded.model_fingerprint,
                    creation_timestamp=excluded.creation_timestamp,
                    source_content_hash=excluded.source_content_hash,
                    status=excluded.status,
                    confidence_classification=excluded.confidence_classification,
                    embedding_vector=excluded.embedding_vector
            """, (
                card_id,
                provider_meta["provider"],
                provider_meta["model"],
                provider_meta["vector_dimension"],
                provider_meta["model_fingerprint"],
                creation_timestamp,
                content_hash,
                "active",
                provider_meta["confidence_classification"],
                embedding_json
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error in upsert_card: {e}")
            return False
        finally:
            conn.close()

    def update_card_confidence(self, card_id: str, outcome: str, learning_rate: float = 0.05) -> Tuple[bool, float]:
        """
        Dynamically scales the confidence score of a SOK card based on success/failure outcomes.
        Clips score strictly inside the stable boundary of [0.1, 2.0].
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT confidence, is_canonical FROM knowledge_cards WHERE card_id = ?", (card_id,))
            row = cursor.fetchone()
            if not row:
                return False, 1.0

            old_confidence = row[0]
            is_canonical = row[1]

            # Opt 5: Canonical cards are immune to dynamic confidence degradation to remain stable anchors
            if is_canonical:
                return True, old_confidence

            # Apply reinforcement factor
            if outcome == "success":
                new_confidence = old_confidence * (1.0 + learning_rate)
            elif outcome == "failure":
                new_confidence = old_confidence * (1.0 - learning_rate)
            else:
                new_confidence = old_confidence

            # Enforce strict confidence boundaries [0.1, 2.0]
            new_confidence = max(0.1, min(2.0, new_confidence))

            cursor.execute("UPDATE knowledge_cards SET confidence = ? WHERE card_id = ?", (new_confidence, card_id))
            conn.commit()
            return True, float(round(new_confidence, 4))
        except sqlite3.Error:
            return False, 1.0
        finally:
            conn.close()

    def run_maintenance(self) -> bool:
        """
        Opt 6: Background DB maintenance (Vacuum & Optimize)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA optimize;")
            cursor.execute("VACUUM;")
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def add_link(self, source_id: str, target_id: str, relationship_type: str) -> bool:
        """
        Creates a directed link between SOK cards (e.g. DEPENDS_ON, ENHANCES).
        """
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

    def get_card(self, card_id: str) -> Dict[str, Any]:
        """
        Retrieves a single card with its direct link metadata and confidence score.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        card = None
        try:
            cursor.execute("SELECT * FROM knowledge_cards WHERE card_id = ? AND is_deleted = 0", (card_id,))
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
        return card

    def get_all_cards(self) -> List[Dict[str, Any]]:
        """
        Retrieves all SOK cards stored in the database.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cards = []
        try:
            cursor.execute("SELECT * FROM knowledge_cards WHERE is_deleted = 0")
            for row in cursor.fetchall():
                card = dict(row)
                if card["embedding"]:
                    card["embedding"] = json.loads(card["embedding"])
                cards.append(card)
        except sqlite3.Error:
            pass
        finally:
            conn.close()
        return cards

    @functools.lru_cache(maxsize=256)
    def _get_query_keywords(self, query: str) -> Tuple[str, ...]:
        return tuple(set(w for w in query.lower().replace(",", " ").replace(".", " ").split() if len(w) > 3))

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a hybrid cosine similarity search against cached embeddings + basic keyword overlap.
        Opt 14: Exact Match short-circuiting.
        Opt 13: Query norm caching.
        """
        query_vector = self.compute_local_embedding(query)
        query_norm = math.sqrt(sum(q ** 2 for q in query_vector)) # Opt 13
        query_keywords = self._get_query_keywords(query)
        meta = self.embedding_provider.get_metadata()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        results = []
        try:
            cursor.execute("""
                SELECT kc.card_id, kc.family, kc.focus, kc.content, kc.confidence, kc.embedding as fallback_embedding,
                       ce.embedding_vector as preferred_embedding, ce.provider
                FROM knowledge_cards kc
                LEFT JOIN card_embeddings ce ON kc.card_id = ce.card_id AND ce.provider = ? AND ce.model = ?
                WHERE kc.is_deleted = 0
            """, (meta["provider"], meta["model"]))

            for row in cursor.fetchall():
                card = dict(row)
                content_lower = card["content"].lower()

                # Hybrid Keyword Overlap (Opt 8)
                overlap_count = sum(1 for kw in query_keywords if kw in content_lower)
                keyword_boost = min(0.15, overlap_count * 0.03) # Max 15% boost

                use_fallback = False
                if card.get("preferred_embedding"):
                    card_vector = json.loads(card["preferred_embedding"])
                    if len(card_vector) != len(query_vector):
                        use_fallback = True
                else:
                    use_fallback = True

                if use_fallback:
                    if not card["fallback_embedding"]:
                        continue
                    card_vector = json.loads(card["fallback_embedding"])
                    if len(card_vector) != len(query_vector):
                        from solomon_embeddings import DeterministicHashProvider
                        fallback_query_vector = DeterministicHashProvider().embed_texts([query])[0]
                        actual_query_vector = fallback_query_vector
                        actual_query_norm = math.sqrt(sum(q ** 2 for q in actual_query_vector))
                    else:
                        actual_query_vector = query_vector
                        actual_query_norm = query_norm
                else:
                    actual_query_vector = query_vector
                    actual_query_norm = query_norm

                dot_product = sum(q * c for q, c in zip(actual_query_vector, card_vector))
                card_norm = math.sqrt(sum(c ** 2 for c in card_vector))

                denom = actual_query_norm * card_norm
                if denom < 1e-9:
                    similarity = 0.0
                else:
                    similarity = dot_product / denom

                similarity = max(-1.0, min(1.0, similarity))

                # Opt 14: Exact match short circuit (saves processing the rest of DB if a 1.0 is found)
                if similarity >= 0.999:
                    return [{
                        "card_id": card["card_id"],
                        "family": card["family"],
                        "focus": card["focus"],
                        "content": card["content"],
                        "confidence": card["confidence"],
                        "similarity": 1.0,
                        "embedding_type": "preferred" if not use_fallback else "fallback"
                    }]

                # Apply hybrid boost
                final_score = min(1.0, similarity + keyword_boost)

                results.append({
                    "card_id": card["card_id"],
                    "family": card["family"],
                    "focus": card["focus"],
                    "content": card["content"],
                    "confidence": card["confidence"],
                    "similarity": round(float(final_score), 4),
                    "embedding_type": "preferred" if not use_fallback else "fallback"
                })
        except sqlite3.Error as e:
            print(f"Search DB error: {e}")
        finally:
            conn.close()

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
