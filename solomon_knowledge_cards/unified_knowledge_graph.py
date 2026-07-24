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
            # Phase 42: Ternary Weights (-1, 0, 1) mapping
            t_weight = 1 if weight > 0.5 else (-1 if weight < -0.5 else 0)
            self.edges[source_id].append({"target": target_id, "rel": relationship, "weight": t_weight})

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        self._prune_expired()
        neighbors = self.edges.get(node_id, [])
        return sorted(neighbors, key=lambda x: x.get("weight", 0), reverse=True)

    def get_subgraph_bfs(self, start_id: str, max_depth: int = 2) -> List[str]:
        self._prune_expired()
        if start_id not in self.nodes: return []
        visited = set([start_id])
        queue = [(start_id, 0)]
        result = [start_id]
        while queue:
            curr_id, depth = queue.pop(0)
            if depth >= max_depth: continue
            for edge in self.get_neighbors(curr_id):
                neighbor = edge["target"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
                    result.append(neighbor)
        return result

    def _prune_expired(self):
        expired_ids = [n_id for n_id, node in self.nodes.items() if node.is_expired()]
        for e_id in expired_ids: self.remove_node(e_id)

    # Phase 34: Semantic Eviction Strategy
    def evict_by_semantic_distance(self, target_id: str, max_nodes: int):
        if len(self.nodes) <= max_nodes: return
        # Simple implementation: evict nodes furthest chronologically as proxy for semantic distance stub
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.timestamp)
        while len(self.nodes) > max_nodes and sorted_nodes:
            oldest = sorted_nodes.pop(0)
            if oldest.node_id != target_id:
                self.remove_node(oldest.node_id)

    def remove_node(self, e_id: str):
        if e_id in self.nodes: del self.nodes[e_id]
        if e_id in self.edges: del self.edges[e_id]
        for src, edges in self.edges.items():
            self.edges[src] = [e for e in edges if e["target"] != e_id]

    def ingest_federated_graph(self, remote_nodes: Dict[str, Any], remote_edges: Dict[str, Any]): pass

class UnifiedEmbeddingEngine:
    def __init__(self):
        self.cache: Dict[str, List[float]] = {}
    def embed_text(self, text: str, quantize_to_8bit: bool = True) -> List[Any]:
        embedding = [(hash(text + str(i)) % 1000) / 1000.0 for i in range(16)]
        self.cache[text] = embedding
        return [int(v * 127) for v in embedding] if quantize_to_8bit else embedding
    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2: return 0.0
        dot, mag1, mag2 = sum(a * b for a, b in zip(vec1, vec2)), math.sqrt(sum(a * a for a in vec1)), math.sqrt(sum(b * b for b in vec2))
        return dot / (mag1 * mag2) if mag1 and mag2 else 0.0
