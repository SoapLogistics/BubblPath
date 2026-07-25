import uuid
import time
import json
import math
import logging
from typing import Dict, Any, List, Optional
from solomon_memory.db_manager import DatabaseManager
from solomon_core.event_bus import CognitiveEventBus
from solomon_memory.models.schema import initialize_schema
from solomon_memory.graph.embeddings import EmbeddingGenerator

logger = logging.getLogger("MnemosyneEngine")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate the cosine similarity between two vectors."""
    if not v1 or not v2: return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    return dot_product / (norm_v1 * norm_v2) if norm_v1 and norm_v2 else 0.0

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

        results = []
        for row in rows:
            if not row["vector_embedding"]: continue
            card_vector = json.loads(row["vector_embedding"])
            sim = cosine_similarity(query_vector, card_vector)
            if sim >= threshold:
                results.append({"card_id": row["card_id"], "content": row["content"], "similarity": sim})

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def purge_expired_memories(self):
        current_time = int(time.time())
        query = "DELETE FROM sok_cards WHERE ttl_expires_at <= ?"
        self.db.execute_query(query, (current_time,))
        logger.info("Purged expired SOK memories.")
