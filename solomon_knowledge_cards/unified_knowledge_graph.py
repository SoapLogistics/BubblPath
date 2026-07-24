import math
from typing import Dict, Any, List, Optional
import time

class GraphNode:
    def __init__(self, node_id: str, node_type: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        self.node_id = node_id
        self.node_type = node_type
        self.data = data
        self.timestamp = time.time()
        self.quantized_embedding: Optional[List[int]] = None
        # Phase 5: TTL Node Pruning
        self.expires_at = time.time() + ttl_seconds if ttl_seconds else None

    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class UniversalKnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, List[Dict[str, str]]] = {}

    def add_node(self, node: GraphNode):
        self._prune_expired()
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []

    def link_nodes(self, source_id: str, target_id: str, relationship: str):
        self._prune_expired()
        if source_id in self.nodes and target_id in self.nodes:
            self.edges[source_id].append({"target": target_id, "rel": relationship})

    def get_neighbors(self, node_id: str) -> List[Dict[str, str]]:
        self._prune_expired()
        return self.edges.get(node_id, [])

    # Phase 4: Subgraph BFS Querying
    def get_subgraph_bfs(self, start_id: str, max_depth: int = 2) -> List[str]:
        self._prune_expired()
        if start_id not in self.nodes:
            return []

        visited = set([start_id])
        queue = [(start_id, 0)]
        result = [start_id]

        while queue:
            curr_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            for edge in self.edges.get(curr_id, []):
                neighbor = edge["target"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
                    result.append(neighbor)

        return result

    # Phase 5: TTL Enforcement
    def _prune_expired(self):
        expired_ids = [n_id for n_id, node in self.nodes.items() if node.is_expired()]
        for e_id in expired_ids:
            del self.nodes[e_id]
            if e_id in self.edges:
                del self.edges[e_id]
            # Prune dangling edges
            for src, edges in self.edges.items():
                self.edges[src] = [e for e in edges if e["target"] != e_id]

class UnifiedEmbeddingEngine:
    def __init__(self):
        self.cache: Dict[str, List[float]] = {}

    def embed_text(self, text: str, quantize_to_8bit: bool = True) -> List[Any]:
        embedding = [(hash(text + str(i)) % 1000) / 1000.0 for i in range(16)]
        self.cache[text] = embedding
        if quantize_to_8bit:
            return [int(v * 127) for v in embedding]
        return embedding

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2) or len(vec1) == 0: return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1, mag2 = math.sqrt(sum(a * a for a in vec1)), math.sqrt(sum(b * b for b in vec2))
        return dot / (mag1 * mag2) if mag1 and mag2 else 0.0
