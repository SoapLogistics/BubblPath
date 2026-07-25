"""
Topological Data Analysis (TDA) Engine (solomon_tda.py)
-------------------------------------------------------
Implements persistent homology approximation to understand the "shape"
of memory graphs. Detects 0D features (knowledge clusters) and 1D
features (semantic voids / missing knowledge gaps) mathematically using
pure Python Vietoris-Rips complex approximation.
"""

import math
from typing import List, Tuple, Dict, Set

Vector = Tuple[float, ...]

class TDAEngine:
    def __init__(self):
        pass

    def _euclidean_distance(self, v1: Vector, v2: Vector) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def build_vietoris_rips_graph(self, points: List[Vector], epsilon: float) -> Dict[int, List[int]]:
        """Builds a graph where edges exist if distance between points <= epsilon."""
        graph = {i: [] for i in range(len(points))}
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                if self._euclidean_distance(points[i], points[j]) <= epsilon:
                    graph[i].append(j)
                    graph[j].append(i)
        return graph

    def _find_connected_components(self, graph: Dict[int, List[int]]) -> List[Set[int]]:
        """Finds 0-dimensional topological features (clusters)."""
        visited = set()
        components = []

        for node in graph:
            if node not in visited:
                component = set()
                queue = [node]
                while queue:
                    current = queue.pop(0)
                    if current not in visited:
                        visited.add(current)
                        component.add(current)
                        queue.extend([n for n in graph[current] if n not in visited])
                components.append(component)

        return components

    def _find_cycles(self, graph: Dict[int, List[int]]) -> List[List[int]]:
        """
        Approximates 1-dimensional topological features (voids/holes).
        Finds simple cycles using DFS backtracking.
        """
        cycles = []
        visited = set()

        def dfs(start, current, path):
            visited.add(current)
            for neighbor in graph[current]:
                if neighbor == start and len(path) > 2:
                    cycles.append(path + [neighbor])
                elif neighbor not in visited:
                    dfs(start, neighbor, path + [neighbor])
            visited.remove(current)

        for node in graph:
            dfs(node, node, [node])
            visited.add(node) # Prevent finding the same cycle from different start points

        return cycles

    def analyze_topology(self, memory_points: List[Vector], epsilon: float) -> Dict[str, int]:
        """
        Analyzes the topology of a set of memory vectors at a specific distance scale (epsilon).
        Returns the Betti numbers: B0 (clusters) and B1 (voids).
        """
        if not memory_points:
            return {"clusters_b0": 0, "voids_b1": 0}

        graph = self.build_vietoris_rips_graph(memory_points, epsilon)

        clusters = self._find_connected_components(graph)
        cycles = self._find_cycles(graph)

        # B0: Number of connected components
        # B1: Number of independent cycles (approximated here by raw simple cycle count)

        return {
            "clusters_b0": len(clusters),
            "voids_b1": len(cycles) // 2 # Rough heuristic since directed DFS finds reversed duplicates
        }
