import math
from typing import Dict, Any, List, Optional
import time
import hashlib
import random

class GraphNode:
    def __init__(self, node_id: str, node_type: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        self.node_id = node_id
        self.node_type = node_type
        self.data = data
        self.timestamp = time.time()
        self.expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self.embedding = None
        self.temporal_validity = {"start": time.time(), "end": None}
        self.node_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.node_id}{self.node_type}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()

    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class UniversalKnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, List[Dict[str, Any]]] = {}
        self.edge_ledger = []

        # Phase 181: Distributed Hash Table (DHT) Stub
        self.dht_peers = []
        self.local_shard_range = (0, 1000)

    def add_node(self, node: GraphNode):
        self._prune_expired()

        # Phase 181: DHT Routing check
        if not self._is_local_shard(node.node_id):
            self._route_to_peer(node)
            return

        self.nodes[node.node_id] = node
        if node.node_id not in self.edges: self.edges[node.node_id] = []

    def link_nodes(self, source_id: str, target_id: str, relationship: str, weights: List[float] = None, worker_id: str = "system"):
        self._prune_expired()
        if source_id in self.nodes and target_id in self.nodes:

            # Phase 182: Multi-Dimensional Edge Weights
            if not weights:
                weights = [1.0] # Default to 1D

            edge_data = {"target": target_id, "rel": relationship, "weights": weights, "last_traversed": time.time()}
            self.edges[source_id].append(edge_data)

            ledger_entry = {"timestamp": time.time(), "source": source_id, "target": target_id, "rel": relationship, "worker": worker_id}
            ledger_entry["hash"] = hashlib.sha256(str(ledger_entry).encode()).hexdigest()
            self.edge_ledger.append(ledger_entry)

    def _is_local_shard(self, node_id: str) -> bool:
        # Mock logic
        return True

    def _route_to_peer(self, node: GraphNode):
        # Stub for DHT network routing
        pass

    def decay_edges(self):
        current_time = time.time()
        for src, edges in self.edges.items():
            for edge in edges:
                if current_time - edge.get("last_traversed", current_time) > 86400:
                    edge["weights"] = [w * 0.9 for w in edge.get("weights", [1.0])]
            self.edges[src] = [e for e in edges if max([abs(w) for w in e["weights"]]) > 0.05]

    def consolidate_episodic_memory(self, chat_logs: List[Dict[str, str]]):
        import re
        scrubbed = []
        for log in chat_logs:
            c = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', log.get("content", ""))
            scrubbed.append({"role": log.get("role", "system"), "content": c})

        node_id = f"episode_{hash(str(scrubbed))}"
        self.add_node(GraphNode(node_id, "episodic_memory", {"logs": scrubbed}))

    def find_knowledge_gaps(self) -> List[str]:
        return [n for n, e in self.edges.items() if not e]

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        self._prune_expired()
        self.decay_edges()
        # Sort by primary dimension weight
        return sorted(self.edges.get(node_id, []), key=lambda x: x.get("weights", [0])[0], reverse=True)

    # Phase 183: Probabilistic Traversal
    def get_subgraph_markov(self, start_id: str, steps: int = 5) -> List[str]:
        self._prune_expired()
        if start_id not in self.nodes: return []

        path = [start_id]
        curr_id = start_id

        for _ in range(steps):
            neighbors = self.edges.get(curr_id, [])
            if not neighbors: break

            # Select neighbor probabilistically based on primary weight
            weights = [max(0.1, n.get("weights", [0.1])[0]) for n in neighbors]
            total = sum(weights)
            probs = [w/total for w in weights]

            r = random.random()
            cum_p = 0.0
            next_node = neighbors[0]["target"]
            for i, p in enumerate(probs):
                cum_p += p
                if r <= cum_p:
                    next_node = neighbors[i]["target"]
                    break

            path.append(next_node)
            curr_id = next_node

        return path

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

    def compact_memory(self):
        self._prune_expired()

class UnifiedEmbeddingEngine:
    def __init__(self):
        self.cache: Dict[str, List[float]] = {}

    def _product_quantize(self, vector: List[float]) -> List[int]:
        return [int(v * 127) for v in vector]

    def embed_text(self, text: str, context: str = "", quantize_to_1bit: bool = True) -> List[Any]:
        combined = text + context
        embedding = [(hash(combined + str(i)) % 1000) / 1000.0 for i in range(16)]
        if quantize_to_1bit:
            return [1 if v > 0.5 else 0 for v in embedding]
        return embedding

    def similarity(self, vec1: List[int], vec2: List[int]) -> float:
        if not vec1 or not vec2: return 0.0
        dist = sum(el1 != el2 for el1, el2 in zip(vec1, vec2))
        return 1.0 - (dist / len(vec1))
