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
        self.embedding = None # Stored natively now

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
            t_weight = 1 if weight > 0.5 else (-1 if weight < -0.5 else 0)
            self.edges[source_id].append({"target": target_id, "rel": relationship, "weight": t_weight})

    # Phase 67: Graph Convolutional Embeddings
    def update_convolutional_embeddings(self):
        for node_id, node in self.nodes.items():
            if not node.embedding: continue
            neighbors = self.edges.get(node_id, [])
            if not neighbors: continue

            # Simple GCN aggregate: average neighbor embeddings
            sum_emb = list(node.embedding)
            count = 1
            for edge in neighbors:
                n_node = self.nodes.get(edge["target"])
                if n_node and n_node.embedding:
                    for i in range(len(sum_emb)):
                        sum_emb[i] += n_node.embedding[i] * edge.get("weight", 1)
                    count += 1
            node.embedding = [e / count for e in sum_emb]

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        self._prune_expired()
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
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
                    result.append(neighbor)
        return result

    def _prune_expired(self):
        expired_ids = [n_id for n_id, node in self.nodes.items() if node.is_expired()]
        for e_id in expired_ids: self.remove_node(e_id)

    def evict_by_semantic_distance(self, target_id: str, max_nodes: int):
        if len(self.nodes) <= max_nodes: return
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.timestamp)
        while len(self.nodes) > max_nodes and sorted_nodes:
            oldest = sorted_nodes.pop(0)
            if oldest.node_id != target_id: self.remove_node(oldest.node_id)

    def remove_node(self, e_id: str):
        if e_id in self.nodes: del self.nodes[e_id]
        if e_id in self.edges: del self.edges[e_id]
        for src, edges in self.edges.items(): self.edges[src] = [e for e in edges if e["target"] != e_id]

    # Phase 70: Automated Memory Compaction
    def compact_memory(self):
        # Stub for disk level sqlite defragmentation
        self._prune_expired()

class UnifiedEmbeddingEngine:
    def __init__(self):
        self.cache: Dict[str, List[float]] = {}

    # Phase 69: Vector Index Quantization (PQ stub)
    def _product_quantize(self, vector: List[float]) -> List[int]:
        # Compress float32 array into int8 chunks
        return [int(v * 127) for v in vector]

    def embed_text(self, text: str, quantize_to_8bit: bool = True) -> List[Any]:
        embedding = [(hash(text + str(i)) % 1000) / 1000.0 for i in range(16)]
        self.cache[text] = embedding
        return self._product_quantize(embedding) if quantize_to_8bit else embedding

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2: return 0.0
        dot, mag1, mag2 = sum(a * b for a, b in zip(vec1, vec2)), math.sqrt(sum(a * a for a in vec1)), math.sqrt(sum(b * b for b in vec2))
        return dot / (mag1 * mag2) if mag1 and mag2 else 0.0
