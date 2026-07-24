import math
from typing import Dict, Any, List, Optional
import time

class GraphNode:
    """
    Every object in the system (Cards, Projects, Prompts, Repositories,
    Commits, Models, Workers, Research Papers, Sports Strategies) is a GraphNode.
    """
    def __init__(self, node_id: str, node_type: str, data: Dict[str, Any]):
        self.node_id = node_id
        self.node_type = node_type
        self.data = data
        self.timestamp = time.time()
        self.quantized_embedding: Optional[List[int]] = None

class UniversalKnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, List[Dict[str, str]]] = {} # Adjacency list

    def add_node(self, node: GraphNode):
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []

    def link_nodes(self, source_id: str, target_id: str, relationship: str):
        if source_id in self.nodes and target_id in self.nodes:
            self.edges[source_id].append({"target": target_id, "rel": relationship})

    def get_neighbors(self, node_id: str) -> List[Dict[str, str]]:
        return self.edges.get(node_id, [])

class UnifiedEmbeddingEngine:
    """
    One embedding engine. One cache. One API. One similarity service.
    """
    def __init__(self):
        self.cache: Dict[str, List[float]] = {}

    def embed_text(self, text: str, quantize_to_8bit: bool = True) -> List[Any]:
        # Simple deterministic hashing based embedding for illustration
        embedding = [
            (hash(text + str(i)) % 1000) / 1000.0 for i in range(16)
        ]
        self.cache[text] = embedding
        if quantize_to_8bit:
            return self._quantize_8bit(embedding)
        return embedding

    def _quantize_8bit(self, vector: List[float]) -> List[int]:
        return [int(v * 127) for v in vector]

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2) or len(vec1) == 0:
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)
