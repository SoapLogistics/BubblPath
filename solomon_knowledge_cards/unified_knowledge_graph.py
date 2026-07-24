import math
from typing import Dict, Any, List, Optional
import time

class GraphNode:
    def __init__(self, node_id: str, node_type: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        self.node_id = node_id
        self.node_type = node_type
        self.data = data
        self.timestamp = time.time()
        self.expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self.embedding = None
        self.temporal_validity = {"start": time.time(), "end": None} # Phase 92: Temporal Graph Tracking

    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class UniversalKnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, List[Dict[str, Any]]] = {}

    def add_node(self, node: GraphNode):
        self._prune_expired()
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges: self.edges[node.node_id] = []

    def link_nodes(self, source_id: str, target_id: str, relationship: str, weight: float = 1.0):
        self._prune_expired()
        if source_id in self.nodes and target_id in self.nodes:
            # Phase 100: Hallucination Graphing (Negative Weights)
            t_weight = weight if relationship != "hallucinated" else -1.0
            self.edges[source_id].append({"target": target_id, "rel": relationship, "weight": t_weight, "last_traversed": time.time()})

    # Phase 96: Graph Forgetting via Decay
    def decay_edges(self):
        current_time = time.time()
        for src, edges in self.edges.items():
            for edge in edges:
                # If not traversed in 24h, reduce weight
                if current_time - edge.get("last_traversed", current_time) > 86400:
                    edge["weight"] *= 0.9
            # Remove snapped edges
            self.edges[src] = [e for e in edges if abs(e["weight"]) > 0.05]

    # Phase 91: Episodic Memory Consolidation
    def consolidate_episodic_memory(self, chat_logs: List[Dict[str, str]]):
        # Convert list of dicts to a single abstract graph node stub
        node_id = f"episode_{hash(str(chat_logs))}"
        self.add_node(GraphNode(node_id, "episodic_memory", {"logs": chat_logs}))

    # Phase 93: Topological Data Analysis stub
    def find_knowledge_gaps(self) -> List[str]:
        # Returns nodes with 0 edges
        return [n for n, e in self.edges.items() if not e]

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        self._prune_expired()
        self.decay_edges()
        return sorted(self.edges.get(node_id, []), key=lambda x: x.get("weight", 0), reverse=True)

    def get_subgraph_bfs(self, start_id: str, max_depth: int = 2) -> List[str]:
        self._prune_expired()
        if start_id not in self.nodes: return []
        visited, queue, result = set([start_id]), [(start_id, 0)], [start_id]
        while queue:
            curr_id, depth = queue.pop(0)
            if depth >= max_depth: continue
            for edge in self.get_neighbors(curr_id):
                neighbor = edge["target"]
                edge["last_traversed"] = time.time() # update traversal
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
                    result.append(neighbor)
        return result

    def _prune_expired(self):
        expired_ids = [n_id for n_id, node in self.nodes.items() if node.is_expired()]
        for e_id in expired_ids: self.remove_node(e_id)

    def remove_node(self, e_id: str):
        if e_id in self.nodes: del self.nodes[e_id]
        if e_id in self.edges: del self.edges[e_id]
        for src, edges in self.edges.items(): self.edges[src] = [e for e in edges if e["target"] != e_id]

class UnifiedEmbeddingEngine:
    def __init__(self):
        self.cache: Dict[str, List[float]] = {}

    # Phase 89: Quantized Embedding Search (QES) - Hamming Distance on 1-bit hashes
    def _hamming_distance(self, vec1: List[int], vec2: List[int]) -> int:
        return sum(el1 != el2 for el1, el2 in zip(vec1, vec2))

    def embed_text(self, text: str, context: str = "", quantize_to_1bit: bool = True) -> List[Any]:
        # Phase 97: Context-Aware Embeddings (modifying hash based on context string)
        combined = text + context
        embedding = [(hash(combined + str(i)) % 1000) / 1000.0 for i in range(16)]

        if quantize_to_1bit:
            return [1 if v > 0.5 else 0 for v in embedding]
        return embedding

    def similarity(self, vec1: List[int], vec2: List[int]) -> float:
        # returns similarity based on hamming distance
        if not vec1 or not vec2: return 0.0
        dist = self._hamming_distance(vec1, vec2)
        return 1.0 - (dist / len(vec1))
