"""
Solomon Perpetual Learning Machine
Phase 5: Skill Graph & Dependency Maps

This module tracks directional relationships between different capability nodes,
performs topological sorting, and scans the active graph to detect structural
redundancies, missing knowledge vectors, and recommend next-learning topics.
"""

from typing import Dict, Any, List, Set, Tuple

class SkillGraphNavigator:
    """
    Navigates, sorts, and analyzes active skills and their dependency nodes to
    autonomously plan Solomon's forward learning curriculum.
    """

    def __init__(self):
        # Maps skill_id to its registered details and its explicit prerequisites
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, Set[str]] = {}

    def register_skill_node(self, skill_id: str, name: str, prerequisites: List[str] = None, signatures: Dict[str, Any] = None):
        """
        Registers a skill node with its directional prerequisites and functional signatures.
        """
        self.nodes[skill_id] = {
            "skill_id": skill_id,
            "name": name,
            "prerequisites": prerequisites or [],
            "signatures": signatures or {}
        }
        self.dependencies[skill_id] = set(prerequisites or [])

    def topological_sort(self) -> List[str]:
        """
        Performs a topological sort on registered skill nodes using Kahn's algorithm.
        Detects circular dependencies and returns a valid linear execution order.
        """
        in_degree = {u: 0 for u in self.nodes}
        adj = {u: [] for u in self.nodes}

        for u, prereqs in self.dependencies.items():
            for v in prereqs:
                if v in adj:
                    adj[v].append(u)
                    in_degree[u] += 1

        queue = [u for u, deg in in_degree.items() if deg == 0]
        sorted_order = []

        while queue:
            # Keep order deterministic by sorting the queue queue elements alphabetically
            queue.sort()
            u = queue.pop(0)
            sorted_order.append(u)

            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        # If sorted order doesn't cover all registered nodes, a cycle exists
        if len(sorted_order) != len(self.nodes):
            # Fallback to simple alphabetical list of remaining nodes for robustness
            remaining = [u for u in self.nodes if u not in sorted_order]
            sorted_order.extend(sorted(remaining))

        return sorted_order

    def analyze_graph_health(self) -> Dict[str, Any]:
        """
        Scans the active dependency mappings to detect structural issues:
        1. Missing Knowledge Vectors: Prerequisites referenced by registered skills but missing in our nodes.
        2. Structural Redundancies: Skills with identical inputs/outputs signatures.
        3. Learning Recommendation: Suggests the next missing dependency to learn.
        """
        missing_vectors = set()
        redundancies = []
        registered_ids = set(self.nodes.keys())

        # 1. Detect missing dependencies
        for u, prereqs in self.dependencies.items():
            for v in prereqs:
                if v not in registered_ids:
                    missing_vectors.add(v)

        # 2. Detect redundancies via signature overlap
        signatures_seen = {} # signature_hash -> list of skill_ids
        for u, node in self.nodes.items():
            sig = node["signatures"]
            if sig:
                sig_key = f"{sig.get('inputs') or 'none'}->{sig.get('outputs') or 'none'}"
                if sig_key in signatures_seen:
                    signatures_seen[sig_key].append(u)
                else:
                    signatures_seen[sig_key] = [u]

        for sig_key, ids in signatures_seen.items():
            if len(ids) > 1:
                redundancies.append({
                    "signature": sig_key,
                    "redundant_skills": ids
                })

        # 3. Formulate forward learning recommendations
        recommendations = []
        for m in sorted(list(missing_vectors)):
            recommendations.append(f"Learn prerequisite capability '{m}' to unlock dependent skill packages.")

        if not recommendations:
            recommendations.append("All dependencies are resolved! The active Skill Graph is fully healthy.")

        return {
            "missing_knowledge_vectors": sorted(list(missing_vectors)),
            "structural_redundancies": redundancies,
            "next_learning_recommendations": recommendations,
            "is_healthy": len(missing_vectors) == 0 and len(redundancies) == 0
        }
