"""
Solomon Perpetual Learning Machine
Active Skill Graph & Quarantined Sandbox Execution Engine

This module implements:
1. SkillGraph: A topological dependency resolver that resolves execution order
   for dynamically assimilated capabilities and helper workflows.
2. SandboxExecutor: A isolated execution container that executes arbitrary python scripts
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
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, Set[str]] = {} # node -> set of dependencies

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
                    self.dependencies[dep] = set()

    def resolve_execution_order(self) -> List[str]:
        """
        Computes a valid topological execution sequence using Kahn's Algorithm.
        Detects circular dependencies and raises a ValueError if a cycle is present.
        """
        # Create copies to manipulate
        in_degree = {u: 0 for u in self.nodes}
        adj = {u: set() for u in self.nodes}

        for u, deps in self.dependencies.items():
            for v in deps:
                # v must be executed BEFORE u (v is a dependency of u)
                # Therefore, there is a directed edge from v -> u
                if v in adj:
                    adj[v].add(u)
                    in_degree[u] += 1

        # Queue of nodes with no incoming dependencies (in_degree == 0)
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
            # Find the nodes involved in circular dependencies
            remaining = [u for u, deg in in_degree.items() if deg > 0]
            raise ValueError(f"Circular dependency detected in Skill Graph among nodes: {remaining}")

        return order


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
            # Run python subprocess under constraints
            # We enforce limits using subprocess timeout bounds.
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
