import uuid
import time
import logging
from typing import Dict, Any, List
from solomon_memory.db_manager import DatabaseManager
from solomon_core.event_bus import CognitiveEventBus
from solomon_memory.models.schema import initialize_schema

logger = logging.getLogger("MnemosyneEngine")

class MnemosyneGraphEngine:
    """
    Advanced Graph-Relational Engine for Project Solomon.
    Implements TTL expiration, multi-dimensional edge weights, and vector cluster routing.
    """
    def __init__(self):
        self.db = DatabaseManager()
        self.bus = CognitiveEventBus()
        initialize_schema()

    def store_card(self, content: str, ttl_seconds: int = 86400, cluster_id: int = 0) -> str:
        card_id = f"sok_{uuid.uuid4().hex[:12]}"
        expires_at = int(time.time()) + ttl_seconds

        query = "INSERT INTO sok_cards (card_id, content, embedding_cluster, ttl_expires_at) VALUES (?, ?, ?, ?)"
        self.db.execute_query(query, (card_id, content, cluster_id, expires_at))

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

    def purge_expired_memories(self):
        current_time = int(time.time())
        query = "DELETE FROM sok_cards WHERE ttl_expires_at <= ?"
        self.db.execute_query(query, (current_time,))
        logger.info("Purged expired SOK memories.")
