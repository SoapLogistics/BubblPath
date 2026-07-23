"""
Solomon SOSS Phase 5: Skill Graph & Dependency Maps

This module organizes dynamically generated Skill Packages into a directed dependency graph.
It resolves execution sequences using topological sorting and identifies knowledge gaps or
structural redundancies.
"""

from typing import List, Dict, Set, Tuple, Any


class SkillGraph:
    """
    Manages direct dependencies between skills and maps learning paths.
    """
    def __init__(self):
        self.skills: Set[str] = set()
        # adjacency list: skill_name -> set of prerequisite skill_names (dependencies)
        self.dependencies: Dict[str, Set[str]] = {}
        # relationship tags: (skill_from, skill_to) -> relationship_type ("DEPENDS_ON", "ENHANCES")
        self.relations: Dict[Tuple[str, str], str] = {}

    def add_skill(self, skill_name: str):
        """
        Registers a new skill node in the graph.
        """
        self.skills.add(skill_name)
        if skill_name not in self.dependencies:
            self.dependencies[skill_name] = set()

    def add_dependency(self, skill_name: str, depends_on: str, relationship_type: str = "DEPENDS_ON"):
        """
        Creates a directed edge between two skills.
        """
        self.add_skill(skill_name)
        self.add_skill(depends_on)
        self.dependencies[skill_name].add(depends_on)
        self.relations[(skill_name, depends_on)] = relationship_type

    def detect_cycles_dfs(self) -> List[str]:
        """
        Detects if there are recursive/circular dependency cycles in the skill graph.
        Returns the cycle path list if a cycle is found, empty list otherwise.
        """
        visited = {} # name -> status: 0=unvisited, 1=visiting, 2=visited
        for s in self.skills:
            visited[s] = 0

        path = []

        def dfs(node: str) -> bool:
            visited[node] = 1 # Mark visiting
            path.append(node)
            for neighbor in self.dependencies.get(node, []):
                if visited[neighbor] == 1:
                    # Cycle found!
                    path.append(neighbor)
                    return True
                if visited[neighbor] == 0:
                    if dfs(neighbor):
                        return True
            path.pop()
            visited[node] = 2 # Mark visited
            return False

        for s in self.skills:
            if visited[s] == 0:
                if dfs(s):
                    return path

        return []

    def get_topological_sort(self) -> List[str]:
        """
        Computes the topological sorting of skills to define a valid execution sequence.
        Raises ValueError if a cycle is detected.
        """
        if self.detect_cycles_dfs():
            raise ValueError("Circular dependency detected in the Skill Graph. Cannot resolve topological sort.")

        visited = set()
        stack = []

        def dfs(node: str):
            visited.add(node)
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
            stack.append(node)

        for s in self.skills:
            if s not in visited:
                dfs(s)

        return stack # Returns prerequisites first

    def find_missing_prerequisites(self, active_skills: Set[str]) -> Set[str]:
        """
        Identifies dependencies that exist in the graph but are missing from the system's
        actively compiled skill-base (representing knowledge gaps).
        """
        gaps = set()
        for s in self.skills:
            for dep in self.dependencies.get(s, []):
                if dep not in active_skills:
                    gaps.add(dep)
        return gaps

    def get_graph_analytics(self) -> Dict[str, Any]:
        """
        Audits graph state to discover bottlenecks, isolated nodes, or path length metrics.
        """
        bottlenecks = []
        # Find nodes with most incoming edges (meaning many things depend on them)
        dependency_counts = {}
        for s in self.skills:
            dependency_counts[s] = 0

        for s in self.skills:
            for dep in self.dependencies.get(s, []):
                if dep in dependency_counts:
                    dependency_counts[dep] += 1

        sorted_deps = sorted(dependency_counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_deps:
            max_deps = sorted_deps[0][1]
            # Anything with max or close to max dependency can be considered a bottleneck
            bottlenecks = [item[0] for item in sorted_deps if item[1] >= max(max_deps, 1)]

        return {
            "total_skills": len(self.skills),
            "total_dependencies": len(self.relations),
            "bottlenecks": bottlenecks,
            "has_cycles": len(self.detect_cycles_dfs()) > 0
        }
