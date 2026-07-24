import threading
import time
import sqlite3
from typing import Optional
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_embeddings import DenseEmbeddingProvider
import json
import datetime
import hashlib

class AsyncEmbeddingWorker:
    def __init__(self, db_path: str = "solomon_mnemosyne_demo.db", batch_size: int = 10, interval_sec: int = 5):
        self.db_path = db_path
        self.batch_size = batch_size
        self.interval_sec = interval_sec
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.provider = DenseEmbeddingProvider()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=self.interval_sec + 2)

    def _worker_loop(self):
        while self.running:
            self.process_batch()
            time.sleep(self.interval_sec)

    def process_batch(self):
        """Finds cards lacking dense embeddings and processes them."""
        # Only process if dense embeddings are available
        meta = self.provider.get_metadata()
        if meta["provider"] == "deterministic_hash":
            return # Skip if only fallback is available

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Find cards that don't have an embedding from this specific provider/model
            # or where the content hash doesn't match the source_content_hash
            cursor.execute("""
                SELECT kc.card_id, kc.content
                FROM knowledge_cards kc
                LEFT JOIN card_embeddings ce ON kc.card_id = ce.card_id
                    AND ce.provider = ? AND ce.model = ?
                WHERE ce.card_id IS NULL OR ce.source_content_hash != (
                    -- this is a bit tricky to do in pure SQLite without a custom func,
                    -- so we'll just check if it's missing or re-hash in python
                    NULL
                )
                LIMIT ?
            """, (meta["provider"], meta["model"], self.batch_size))

            rows = cursor.fetchall()

            # Additional pass to find cards where the hash has changed
            if len(rows) < self.batch_size:
                cursor.execute("""
                    SELECT kc.card_id, kc.content, ce.source_content_hash
                    FROM knowledge_cards kc
                    JOIN card_embeddings ce ON kc.card_id = ce.card_id
                        AND ce.provider = ? AND ce.model = ?
                """, (meta["provider"], meta["model"]))
                for row in cursor.fetchall():
                    content = row["content"]
                    current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    if current_hash != row["source_content_hash"]:
                        rows.append(row)
                        if len(rows) >= self.batch_size:
                            break

            if not rows:
                return

            texts = [row["content"] for row in rows]
            card_ids = [row["card_id"] for row in rows]

            embeddings = self.provider.embed_texts(texts)
            creation_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

            for i, card_id in enumerate(card_ids):
                emb_json = json.dumps(embeddings[i])
                content_hash = hashlib.sha256(texts[i].encode("utf-8")).hexdigest()

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
                    meta["provider"],
                    meta["model"],
                    meta["vector_dimension"],
                    meta["model_fingerprint"],
                    creation_timestamp,
                    content_hash,
                    "active",
                    meta["confidence_classification"],
                    emb_json
                ))

            conn.commit()

        except sqlite3.Error as e:
            print(f"Async Embedding Worker DB Error: {e}")
        finally:
            conn.close()
