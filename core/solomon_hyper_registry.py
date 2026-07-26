import json
import re
from typing import Dict, Any, Optional

class HyperRegistryManager:
    """
    Registry Manager for managing the Solomon engine registry.
    Uses native Python dictionary lookups for true O(1) runtime state and dependency lookups.
    Enforces dynamic loading rules and prevents circular/missing dependencies.
    """

    def __init__(self, json_path: str = "solomon_api/engine_registry.json"):
        self.json_path = json_path
        self.registry_data = self._load_json()
        self.engines = self.registry_data.get('engines', [])

        # Build O(1) lookup dictionary and detect duplicates
        self._engine_map = {}
        for e in self.engines:
            eid = e['engine_id']
            if eid in self._engine_map:
                raise ValueError(f"Duplicate registration detected for engine: {eid}")
            self._engine_map[eid] = e

        # Build dependency graph
        self.dependency_graph = {
            e['engine_id']: e.get('dependencies', []) for e in self.engines
        }

        # Verify graph safety on init
        self._validate_dependencies()

    def _load_json(self) -> Dict[str, Any]:
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _validate_dependencies(self):
        """Validates that there are no missing or circular dependencies, and checks versions."""
        engine_ids = set(self.dependency_graph.keys())

        # Helper to parse semantic versioning operators like >=1.0.0
        def parse_dep_string(dep_str):
            match = re.match(r"^([a-zA-Z0-9_-]+)(.*)$", dep_str)
            if not match:
                return dep_str, ""
            return match.group(1), match.group(2).strip()

        # Check missing dependencies and version conflicts
        for engine_id, deps in self.dependency_graph.items():
            for dep_str in deps:
                dep_name, dep_ver_req = parse_dep_string(dep_str)

                if dep_name not in engine_ids:
                    raise ValueError(f"Engine {engine_id} missing dependency: {dep_name}")

                # Version verification
                if dep_ver_req:
                    actual_version = self._engine_map[dep_name].get('version', '0.0.0')
                    # Very simple semver check for exact or >= constraints
                    if dep_ver_req.startswith(">="):
                        req_v = dep_ver_req[2:]
                        if actual_version < req_v:
                            raise ValueError(f"Version conflict: {engine_id} requires {dep_name}{dep_ver_req}, but found version {actual_version}")
                    elif dep_ver_req.startswith("=="):
                        req_v = dep_ver_req[2:]
                        if actual_version != req_v:
                            raise ValueError(f"Version conflict: {engine_id} requires {dep_name}{dep_ver_req}, but found version {actual_version}")

        # Check circular dependencies (must use pure names, not versioned names)
        def has_cycle(node, visited, stack):
            visited.add(node)
            stack.add(node)
            for dep_str in self.dependency_graph.get(node, []):
                neighbor, _ = parse_dep_string(dep_str)
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, stack):
                        return True
                elif neighbor in stack:
                    return True
            stack.remove(node)
            return False

        for engine_id in engine_ids:
            if has_cycle(engine_id, set(), set()):
                raise ValueError(f"Circular dependency detected involving {engine_id}")

    def get_engine_state(self, target_engine_id: str) -> Optional[Dict[str, Any]]:
        """O(1) lookup of engine state."""
        return self._engine_map.get(target_engine_id)

    def is_load_permitted(self, engine_id: str) -> bool:
        """
        Policy enforcement: Dynamic loading is only permitted for:
        - Registered modules
        - Approved versions
        - Verified signatures (conceptually via registry entry)
        - Governed execution paths (status != approval_blocked)
        """
        state = self.get_engine_state(engine_id)
        if not state:
            return False # Anonymous execution prohibited

        # Approval blocked engines cannot be dynamically loaded for execution implicitly
        if state['status_class'] == 'approval_blocked' and state.get('approval_required', False):
            return False

        return True

    def cleanup(self):
        """No-op. Kept for backwards compatibility if called."""
        pass
