import uuid
import time
from typing import Dict, List, Any

import random

class MemoryNode:
    def __init__(self, node_type: str, content: Any, importance: float = 0.5, valence: float = 0.0, arousal: float = 0.0):
        self.id = str(uuid.uuid4())
        self.type = node_type # "Card", "Skill", "Experience", "Failure", "Success", "Project", "Person", "Goal", "Dream"
        self.content = content
        self.creation_time = time.time()
        self.last_accessed = self.creation_time
        self.access_count = 1
        self.importance = importance # Base importance 0.0 to 1.0
        self.layer = "Working" # "Working", "Short-term", "Long-term", "Procedural"

        # Emotional Tagging
        # Valence: -1.0 (Very Negative) to 1.0 (Very Positive)
        # Arousal: 0.0 (Calm) to 1.0 (Highly Stimulated)
        self.valence = valence
        self.arousal = arousal

        # Activation for spreading activation
        self.activation = 0.0

    def access(self):
        self.last_accessed = time.time()
        self.access_count += 1
        self.activation = min(1.0, self.activation + 0.5)

    def decay_activation(self, base_decay_rate: float = 0.1):
        # High arousal reduces decay significantly (flashbulb memories)
        effective_decay = base_decay_rate * (1.0 - (self.arousal * 0.8))
        self.activation = max(0.0, self.activation * (1.0 - effective_decay))

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "layer": self.layer,
            "importance": self.importance,
            "valence": self.valence,
            "arousal": self.arousal,
            "activation": self.activation,
            "access_count": self.access_count
        }

class MemoryEdge:
    def __init__(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type # "is_a", "part_of", "leads_to", "caused_by", "related_to"
        self.weight = weight

    def to_dict(self):
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "weight": self.weight
        }

class UnifiedMemoryGraph:
    def __init__(self):
        self.nodes: Dict[str, MemoryNode] = {}
        self.edges: List[MemoryEdge] = []
        self.adjacency_list: Dict[str, List[MemoryEdge]] = {}

        # Memory Layer thresholds (in seconds)
        self.working_ttl = 300 # 5 minutes
        self.short_term_ttl = 86400 # 1 day

    def add_node(self, node_type: str, content: Any, importance: float = 0.5, valence: float = 0.0, arousal: float = 0.0) -> MemoryNode:
        node = MemoryNode(node_type, content, importance, valence, arousal)
        self.nodes[node.id] = node
        self.adjacency_list[node.id] = []
        return node

    def add_edge(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        if source_id in self.nodes and target_id in self.nodes:
            edge = MemoryEdge(source_id, target_id, relation_type, weight)
            self.edges.append(edge)
            self.adjacency_list[source_id].append(edge)

            # Add reverse edge for undirected traversal or backward spreading
            reverse_edge = MemoryEdge(target_id, source_id, f"rev_{relation_type}", weight * 0.5)
            self.adjacency_list[target_id].append(reverse_edge)

    def ingest(self, node_type: str, content: Any, importance: float = 0.5, valence: float = 0.0, arousal: float = 0.0) -> str:
        """Ingests new information into Working Memory."""
        node = self.add_node(node_type, content, importance, valence, arousal)
        # Attempt semantic linking based on simplistic content overlap (for demonstration)
        self._auto_link(node)
        return node.id

    def _auto_link(self, new_node: MemoryNode):
        """Creates semantic links between the new node and existing nodes."""
        if not isinstance(new_node.content, str):
            return

        new_words = set(new_node.content.lower().split())
        for node_id, node in self.nodes.items():
            if node_id == new_node.id:
                continue
            if isinstance(node.content, str):
                existing_words = set(node.content.lower().split())
                overlap = len(new_words.intersection(existing_words))
                if overlap > 0:
                    similarity = overlap / (len(new_words.union(existing_words)) + 1e-5)
                    if similarity > 0.2:
                        self.add_edge(new_node.id, node.id, "related_to", similarity)

    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recalls context using Spreading Activation."""
        # 1. Initialize activation based on query match
        query_words = set(query.lower().split())
        for node in self.nodes.values():
            node.activation = 0.0
            if isinstance(node.content, str):
                node_words = set(node.content.lower().split())
                overlap = len(query_words.intersection(node_words))
                if overlap > 0:
                    node.activation = min(1.0, overlap / len(query_words))
                    node.access()

        # 2. Spread activation
        spread_steps = 3
        decay = 0.8
        for _ in range(spread_steps):
            new_activations = {node_id: 0.0 for node_id in self.nodes}
            for node_id, node in self.nodes.items():
                if node.activation > 0:
                    new_activations[node_id] += node.activation
                    for edge in self.adjacency_list[node_id]:
                        new_activations[edge.target_id] += node.activation * edge.weight * decay

            # Apply new activations, capped at 1.0
            for node_id, act in new_activations.items():
                self.nodes[node_id].activation = min(1.0, act)

        # 3. Retrieve top activated nodes
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.activation, reverse=True)
        retrieved_nodes = []
        results = []
        for node in sorted_nodes[:top_k]:
            if node.activation > 0.1:
                retrieved_nodes.append(node)
                results.append(node.to_dict())

        # 4. Hebbian Learning: Fire together, wire together
        self._apply_hebbian_learning(retrieved_nodes)

        return results

    def _apply_hebbian_learning(self, activated_nodes: List[MemoryNode]):
        """Strengthens edges between nodes that are activated together during recall."""
        learning_rate = 0.05
        for i in range(len(activated_nodes)):
            for j in range(i + 1, len(activated_nodes)):
                n1 = activated_nodes[i]
                n2 = activated_nodes[j]

                # Find existing edge or create a new weak one
                edge_found = False
                for edge in self.adjacency_list[n1.id]:
                    if edge.target_id == n2.id:
                        # Strengthen existing bond
                        edge.weight = min(1.0, edge.weight + learning_rate)
                        edge_found = True
                        break

                if not edge_found:
                    # Wire them together with a weak associative bond
                    self.add_edge(n1.id, n2.id, "hebbian_association", learning_rate)

    def consolidate(self):
        """
        Moves memory between Working, Short-term, and Long-term layers based on age and access frequency.
        Also handles pruning/forgetting of irrelevant nodes to prevent unbounded disorganization.
        """
        current_time = time.time()
        nodes_to_remove = []

        for node_id, node in self.nodes.items():
            age = current_time - node.creation_time
            time_since_access = current_time - node.last_accessed

            # Decay activation
            node.decay_activation(0.1)

            # State transitions
            if node.layer == "Working":
                if age > self.working_ttl:
                    if node.access_count > 2 or node.importance > 0.7:
                        node.layer = "Short-term"
                    else:
                        nodes_to_remove.append(node_id)
            elif node.layer == "Short-term":
                if age > self.short_term_ttl:
                    if node.access_count > 10 or node.importance > 0.9:
                        node.layer = "Long-term"
                    elif time_since_access > self.short_term_ttl:
                         nodes_to_remove.append(node_id)
            elif node.layer == "Long-term":
                # Long term memory decays very slowly
                if time_since_access > self.short_term_ttl * 7: # 1 week
                    if node.importance < 0.5 and node.access_count < 20:
                        nodes_to_remove.append(node_id)

            # Procedural memory (skills) generally doesn't decay, but gets refined.
            # We skip decay for 'Procedural'

        # Remove forgotten nodes
        for node_id in nodes_to_remove:
            self._remove_node(node_id)

    def dream_cycle(self, max_steps: int = 10):
        """
        Simulates REM sleep consolidation. Performs a random walk, forging distant,
        serendipitous connections and occasionally synthesizing 'Dream' concepts.
        """
        if len(self.nodes) < 3:
            return

        nodes_list = list(self.nodes.values())

        # Pick a random starting point, preferably with high emotional valence/arousal
        start_node = random.choices(
            nodes_list,
            weights=[max(0.1, n.arousal + abs(n.valence)) for n in nodes_list],
            k=1
        )[0]

        current_node = start_node
        path = [current_node]

        for _ in range(max_steps):
            neighbors = self.adjacency_list.get(current_node.id, [])
            if not neighbors:
                # Teleport
                current_node = random.choice(nodes_list)
                path.append(current_node)
                continue

            # Random walk weighted by edge strength
            chosen_edge = random.choices(neighbors, weights=[e.weight for e in neighbors], k=1)[0]
            current_node = self.nodes.get(chosen_edge.target_id)
            if not current_node:
                break
            path.append(current_node)

        # Distant association: Link the start and end of the dream sequence if they are far apart
        if len(path) > 3 and path[0].id != path[-1].id:
            self.add_edge(path[0].id, path[-1].id, "dream_association", 0.3)

            # Occasionally generate a synthesis node
            if random.random() < 0.3 and isinstance(path[0].content, str) and isinstance(path[-1].content, str):
                synthesis_content = f"[DREAM SYNTHESIS] Merging {path[0].type} and {path[-1].type}: '{path[0].content[:20]}...' meets '{path[-1].content[:20]}...'"
                self.ingest("Dream", synthesis_content, importance=0.4, arousal=0.2)

    def _remove_node(self, node_id: str):
        if node_id in self.nodes:
            del self.nodes[node_id]

        # Clean edges
        self.edges = [e for e in self.edges if e.source_id != node_id and e.target_id != node_id]

        # Clean adjacency list
        if node_id in self.adjacency_list:
            del self.adjacency_list[node_id]

        for n_id, edges in self.adjacency_list.items():
            self.adjacency_list[n_id] = [e for e in edges if e.target_id != node_id]

    def get_stats(self):
        stats = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "layers": {
                "Working": 0,
                "Short-term": 0,
                "Long-term": 0,
                "Procedural": 0
            },
            "types": {}
        }
        for node in self.nodes.values():
            stats["layers"][node.layer] += 1
            stats["types"][node.type] = stats["types"].get(node.type, 0) + 1
        return stats
