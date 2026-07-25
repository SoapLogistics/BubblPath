import uuid
import time
import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from solomon_memory.db_manager import DatabaseManager
from solomon_core.event_bus import CognitiveEventBus
from solomon_memory.models.schema import initialize_schema
from solomon_memory.graph.embeddings import EmbeddingGenerator

logger = logging.getLogger("MnemosyneEngine")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate the cosine similarity between two vectors."""
    if not v1 or not v2: return 0.0
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return float(np.dot(vec1, vec2) / (norm1 * norm2)) if norm1 and norm2 else 0.0

class MnemosyneGraphEngine:
    """
    Advanced Graph-Relational Engine for Project Solomon.
    Implements TTL expiration, multi-dimensional edge weights, and vector cluster routing.
    """
    def __init__(self):
        self.db = DatabaseManager()
        self.bus = CognitiveEventBus()
        self.embedder = EmbeddingGenerator()
        initialize_schema()

    def store_card(self, content: str, ttl_seconds: int = 86400, cluster_id: int = 0) -> str:
        card_id = f"sok_{uuid.uuid4().hex[:12]}"
        expires_at = int(time.time()) + ttl_seconds

        # 1. Generate real vector embedding
        vector = self.embedder.get_embedding(content)
        vector_str = json.dumps(vector) if vector else None

        # 2. Store in graph DB
        query = "INSERT INTO sok_cards (card_id, content, vector_embedding, embedding_cluster, ttl_expires_at) VALUES (?, ?, ?, ?, ?)"
        self.db.execute_query(query, (card_id, content, vector_str, cluster_id, expires_at))

        self.bus.publish("MemoryPersisted", {"card_id": card_id, "cluster": cluster_id})
        logger.info(f"Stored SOK card: {card_id} with TTL {ttl_seconds}s")
        return card_id

    def link_cards(self, source_id: str, target_id: str, weight: float = 1.0, semantic_type: str = "RELATES_TO"):
        query = "INSERT OR REPLACE INTO sok_edges (source_id, target_id, edge_weight, semantic_type) VALUES (?, ?, ?, ?)"
        self.db.execute_query(query, (source_id, target_id, weight, semantic_type))
        logger.debug(f"Linked {source_id} -> {target_id} ({semantic_type}) with weight {weight}")

    def retrieve_active_context(self, cluster_id: int) -> List[Dict[str, Any]]:
        current_time = int(time.time())
        # Multi-dimensional active context retrieval with TTL enforcement
        query = """
            SELECT card_id, content FROM sok_cards
            WHERE embedding_cluster = ? AND ttl_expires_at > ?
            ORDER BY created_at DESC LIMIT 50
        """
        rows = self.db.fetch_all(query, (cluster_id, current_time))
        return [{"card_id": row["card_id"], "content": row["content"]} for row in rows]

    def semantic_search(self, query_text: str, top_k: int = 3, threshold: float = 0.75) -> List[Dict[str, Any]]:
        """Performs cosine similarity search against live active context."""
        query_vector = self.embedder.get_embedding(query_text)
        if not query_vector: return []

        current_time = int(time.time())
        query = "SELECT card_id, content, vector_embedding FROM sok_cards WHERE ttl_expires_at > ?"
        rows = self.db.fetch_all(query, (current_time,))

        # Vectorized Matrix Multiplication for massive speed gains over loops
        valid_rows = [row for row in rows if row["vector_embedding"]]
        if not valid_rows: return []

        # Build matrix
        matrix = np.array([json.loads(row["vector_embedding"]) for row in valid_rows])
        q_vec = np.array(query_vector)

        # Normalize
        q_norm = np.linalg.norm(q_vec)
        matrix_norms = np.linalg.norm(matrix, axis=1)

        # Handle zero norms
        if q_norm == 0.0: return []
        matrix_norms[matrix_norms == 0.0] = 1.0 # prevent div by zero

        # Calculate dot products and similarities simultaneously
        dot_products = np.dot(matrix, q_vec)
        similarities = dot_products / (matrix_norms * q_norm)

        results = []
        for i, sim in enumerate(similarities):
            if sim >= threshold:
                results.append({
                    "card_id": valid_rows[i]["card_id"],
                    "content": valid_rows[i]["content"],
                    "similarity": float(sim)
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def purge_expired_memories(self):
        current_time = int(time.time())
        query = "DELETE FROM sok_cards WHERE ttl_expires_at <= ?"
        self.db.execute_query(query, (current_time,))
        logger.info("Purged expired SOK memories.")
