from typing import List, Dict, Any, Optional
import math
from solomon_memory.db_manager import DatabaseManager
from solomon_memory.models.schema import MemoryCardModel

class VectorOps:
    """Utility for basic vector math, avoiding heavy dependencies like numpy where possible."""
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

class MnemosyneEngine:
    """
    Graph-Relational Semantic Memory Engine for Solomon OS.
    Handles semantic search (cosine similarity) and SOK (Structured Object Knowledge) cards.
    """
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()

    def store_memory(self, layer: str, content: str, embedding: List[float], metadata: Dict[str, Any] = None) -> int:
        """Stores a memory card with its vector embedding."""
        query = """
            INSERT INTO memory_cards (layer, content, embedding, metadata)
            VALUES (?, ?, ?, ?)
        """
        import json
        meta_str = json.dumps(metadata) if metadata else "{}"
        emb_str = json.dumps(embedding) # In a purely optimized state, this would be BLOB bytes. JSON is fine for MVP.
        return self.db.execute_write(query, (layer, content, emb_str, meta_str))

    def semantic_search(self, query_embedding: List[float], layer: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most semantically similar memory cards.
        Note: We compute cosine similarity in Python memory. A production vector DB (e.g. pgvector)
        would do this in SQL, but for extreme portability, we process it locally.
        """
        if layer:
            query = "SELECT * FROM memory_cards WHERE layer = ?"
            rows = self.db.execute_query(query, (layer,))
        else:
            query = "SELECT * FROM memory_cards"
            rows = self.db.execute_query(query)

        results = []
        import json
        for row in rows:
            if not row['embedding']:
                continue

            try:
                card_emb = json.loads(row['embedding'])
                sim = VectorOps.cosine_similarity(query_embedding, card_emb)

                # Create a dict from sqlite3.Row
                card_data = dict(row)
                card_data['metadata'] = json.loads(card_data['metadata']) if card_data['metadata'] else {}
                card_data['similarity'] = sim

                results.append(card_data)
            except Exception as e:
                # Log error but continue
                continue

        # Sort by similarity descending
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def consolidate(self):
        """
        Applies decay algorithms to confidence scores and prunes the connectome.
        (Called during Sleep cycles).
        """
        query = """
            UPDATE memory_cards
            SET confidence = confidence * 0.95
            WHERE use_count = 0
            AND julianday('now') - julianday(last_accessed) > 1
        """
        self.db.execute_write(query)
