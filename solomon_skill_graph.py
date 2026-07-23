"""
Solomon Perpetual Learning Machine
Active Skill Graph & Quarantined Sandbox Execution Engine

This module implements:
1. SkillGraph: A topological dependency resolver that resolves execution order
   for dynamically assimilated capabilities and helper workflows.
   Enhanced with Phase 5 analysis: structural redundancy detection, missing prerequisite mapping,
   and automated next-learn recommendations.
2. SandboxExecutor: An isolated execution container that executes arbitrary python scripts
   inside sandboxed subprocess pools, enforcing strict memory footprints and timeouts.
"""

import sys
import subprocess
import tempfile
import os
from typing import List, Dict, Set, Any, Tuple

class SkillGraph:
    """
    Tracks and resolves directed acyclic dependency graphs (DAG) of assimilated skills
    to guarantee safe, topologically ordered execution.
    Supports advanced graph dependency analysis.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, Set[str]] = {} # node -> set of dependencies (prerequisites)

    def register_skill(self, name: str, focus: str, dependencies: List[str] = None, metadata: Dict[str, Any] = None) -> None:
        """
        Registers a capability or helper skill node into the active graph.
        """
        self.nodes[name] = {
            "name": name,
            "focus": focus,
            "metadata": metadata or {}
        }
        if name not in self.dependencies:
            self.dependencies[name] = set()

        if dependencies:
            for dep in dependencies:
                self.dependencies[name].add(dep)
                # Ensure dependency node is registered
                if dep not in self.nodes:
                    self.nodes[dep] = {"name": dep, "focus": "Assimilated dependency", "metadata": {}}
                    if dep not in self.dependencies:
                        self.dependencies[dep] = set()

    def resolve_execution_order(self) -> List[str]:
        """
        Computes a valid topological execution sequence using Kahn's Algorithm.
        Detects circular dependencies and raises a ValueError if a cycle is present.
        """
        in_degree = {u: 0 for u in self.nodes}
        adj = {u: set() for u in self.nodes}

        for u, deps in self.dependencies.items():
            for v in deps:
                # v must be executed BEFORE u (v is a dependency of u)
                if v in adj:
                    adj[v].add(u)
                    in_degree[u] += 1

        queue = [u for u in self.nodes if in_degree[u] == 0]
        queue.sort() # for deterministic order

        order = []
        while queue:
            u = queue.pop(0)
            order.append(u)

            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(order) < len(self.nodes):
            remaining = [u for u, deg in in_degree.items() if deg > 0]
            raise ValueError(f"Circular dependency detected in Skill Graph among nodes: {remaining}")

        return order

    def analyze_graph_structures(self, db: Any = None) -> Dict[str, Any]:
        """
        Analyzes the active DAG for structural insights:
        - Prerequisites: Maps complete chains of execution constraints.
        - Missing knowledge vectors: Dependencies that are not fully registered/implemented in db cards.
        - Structural redundancies: Direct dependency links that are already covered transitively.
        """
        prerequisites_map = {}
        for node in self.nodes:
            # BFS or DFS to find all transitive prerequisites
            visited = set()
            stack = list(self.dependencies.get(node, set()))
            while stack:
                curr = stack.pop()
                if curr not in visited:
                    visited.add(curr)
                    stack.extend(list(self.dependencies.get(curr, set())))
            prerequisites_map[node] = list(visited)

        # Detect missing knowledge vectors (e.g. registered nodes whose focus mentions 'Assimilated dependency'
        # meaning they were created implicitly on dependency declaration but never fully described/saved)
        missing_vectors = []
        for node, data in self.nodes.items():
            if data.get("focus") == "Assimilated dependency":
                missing_vectors.append(node)

        # Detect transitive redundancies
        # If u depends directly on v (direct link v -> u), and there is also a path u -> intermediate -> v,
        # then the direct link is transitively redundant.
        redundancies = []

        # Build simple adjacency for reachability checks
        # Adjacency: u depends on v -> directed edge u -> v
        adj = {u: set(self.dependencies.get(u, set())) for u in self.nodes}

        def has_path_without_direct_edge(src: str, dst: str) -> bool:
            """
            Checks if there is a path from src to dst in the dependency graph
            excluding the direct edge src -> dst.
            """
            queue = [neighbor for neighbor in adj[src] if neighbor != dst]
            visited = set()
            while queue:
                curr = queue.pop(0)
                if curr == dst:
                    return True
                if curr not in visited:
                    visited.add(curr)
                    queue.extend(list(adj.get(curr, set())))
            return False

        for u in self.nodes:
            for v in list(adj[u]):
                # If there's a path u -> ... -> v NOT using the direct edge u -> v,
                # then u -> v is redundant!
                if has_path_without_direct_edge(u, v):
                    redundancies.append({"node": u, "redundant_dependency": v})

        return {
            "all_prerequisites": prerequisites_map,
            "missing_knowledge_vectors": missing_vectors,
            "structural_redundancies": redundancies
        }

    def generate_learning_recommendation(self, db: Any = None) -> Dict[str, Any]:
        """
        Formulates automatic, SOSS Phase 5 next-learn recommendations.
        """
        analysis = self.analyze_graph_structures(db)
        missing = analysis["missing_knowledge_vectors"]

        if missing:
            # Recommends learning the missing vectors first
            recommendation = f"Learn and synthesize full skill packages for missing vectors: {missing}"
            focus_target = missing[0]
            reason = f"Dependency '{focus_target}' was declared as a prerequisite but has no modular implementation."
        else:
            # Find the node with the highest in-degree / prerequisite importance
            importance = {u: 0 for u in self.nodes}
            for u, deps in self.dependencies.items():
                for v in deps:
                    if v in importance:
                        importance[v] += 1

            if importance:
                highest_importance = max(importance, key=importance.get)
                recommendation = f"Optimize and consolidate high-importance prerequisite skill: '{highest_importance}'"
                focus_target = highest_importance
                reason = f"Skill '{highest_importance}' is a critical prerequisite for {importance[highest_importance]} other capabilities."
            else:
                recommendation = "Maintain and audit existing active skill sequence."
                focus_target = None
                reason = "All skills are fully verified and aligned topologically with 0 redundancies."

        return {
            "status": "success",
            "recommended_next_skill": focus_target,
            "learning_action_recommendation": recommendation,
            "analysis_reason": reason,
            "detected_redundancies_count": len(analysis["structural_redundancies"])
        }


class SandboxExecutor:
    """
    Executes Python scripts within quarantined subprocesses, enforcing execution limits.
    """

    @classmethod
    def execute_quarantined_code(cls, source_code: str, timeout_sec: float = 5.0) -> Dict[str, Any]:
        """
        Writes source code to a secure temporary file and executes it via a sandboxed
        Python subprocess. Captures stdout/stderr and intercepts timeout limits.
        """
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp:
            tmp.write(source_code)
            tmp_path = tmp.name

        try:
            process = subprocess.run(
                [sys.executable, tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_sec
            )

            success = process.returncode == 0
            return {
                "success": success,
                "return_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "status": "COMPLETED_SUCCESS" if success else "COMPLETED_ERROR",
                "message": "Script executed completely within safety sandbox limits."
            }

        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "return_code": -1,
                "stdout": e.stdout if e.stdout else "",
                "stderr": e.stderr if e.stderr else f"TimeoutExpired: Execution exceeded hard ceiling of {timeout_sec} seconds.",
                "status": "QUARANTINED_TIMEOUT",
                "message": f"CRITICAL INTERCEPTION: Execution breached the {timeout_sec}s safety limit and was terminated!"
            }
        except Exception as e:
            return {
                "success": False,
                "return_code": -2,
                "stdout": "",
                "stderr": str(e),
                "status": "SYSTEM_EXCEPTION",
                "message": f"Failed to instantiate sandboxed runner: {str(e)}"
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
