import os
import json
import ast
import pytest

def get_python_files(directories):
    files = []
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(".py") and filename != "__init__.py":
                    filepath = os.path.join(root, filename)
                    # Normalize path for cross-platform consistency with JSON
                    files.append(filepath.replace('\\', '/'))
    return files

def has_registry_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id in ['route_key', 'readiness_key', 'internal_parent', 'retired_reason']:
                        return True
    return False

def test_engine_registry_compliance():
    # 1. Load registry JSON
    registry_path = "solomon_api/engine_registry.json"
    assert os.path.exists(registry_path), f"Registry JSON not found at {registry_path}"

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)

    engines = registry_data.get('engines', [])
    registered_engines = {engine['source_path'].replace('\\', '/'): engine for engine in engines}
    exclusions = [exc.replace('\\', '/') for exc in registry_data.get('exclusions', [])]

    # 2. Scan directories for python files
    target_dirs = ["services", "backend/services", "solomon_api"]
    python_files = get_python_files(target_dirs)

    # 3. Assertions
    for py_file in python_files:
        # Check if the file is explicitly excluded
        if py_file in exclusions:
            continue

        # Check if the file is registered in JSON
        assert py_file in registered_engines, f"File {py_file} is not registered in {registry_path} and not in exclusions."

        # Check if file has module-level metadata
        assert has_registry_metadata(py_file), f"File {py_file} is missing mandatory registry metadata (route_key, readiness_key, internal_parent, or retired_reason)"

        engine_metadata = registered_engines[py_file]
        status_class = engine_metadata.get('status_class')

        # Verify specific logic based on status classes
        if status_class == 'active_route':
            assert 'route_paths' in engine_metadata and len(engine_metadata['route_paths']) > 0, f"Engine {engine_metadata['engine_id']} is active_route but missing route_paths"
        elif status_class == 'active_readiness':
            assert 'readiness_keys' in engine_metadata and len(engine_metadata['readiness_keys']) > 0, f"Engine {engine_metadata['engine_id']} is active_readiness but missing readiness_keys"
        elif status_class == 'internal_helper':
            assert 'parent_surface' in engine_metadata and engine_metadata['parent_surface'], f"Engine {engine_metadata['engine_id']} is internal_helper but missing parent_surface"
        elif status_class == 'approval_blocked':
            assert 'refusal_behavior' in engine_metadata and engine_metadata['refusal_behavior'], f"Engine {engine_metadata['engine_id']} is approval_blocked but missing refusal_behavior"

        # Verify non-generated official services have doc/test
        if status_class != 'generated_artifact':
            assert 'doc_path' in engine_metadata and engine_metadata['doc_path'], f"Engine {engine_metadata['engine_id']} is missing doc_path"
            assert 'test_paths' in engine_metadata and len(engine_metadata['test_paths']) > 0, f"Engine {engine_metadata['engine_id']} is missing test_paths"


def test_engine_registry_extended_metadata():
    registry_path = "solomon_api/engine_registry.json"
    import json
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)

    engines = registry_data.get('engines', [])
    for engine in engines:
        engine_id = engine.get('engine_id', 'unknown')
        assert 'version' in engine, f"Engine {engine_id} missing version"
        assert 'description' in engine, f"Engine {engine_id} missing description"
        assert 'inputs' in engine, f"Engine {engine_id} missing inputs"
        assert 'outputs' in engine, f"Engine {engine_id} missing outputs"
        assert 'required_permissions' in engine, f"Engine {engine_id} missing required_permissions"
        assert 'dependencies' in engine, f"Engine {engine_id} missing dependencies"
        assert 'health_state' in engine, f"Engine {engine_id} missing health_state"
        assert 'last_validation_time' in engine, f"Engine {engine_id} missing last_validation_time"
        assert 'ss_classification' in engine, f"Engine {engine_id} missing ss_classification"


def test_dependency_rules():
    registry_path = "solomon_api/engine_registry.json"
    import json
    import re
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)

    engines = registry_data.get('engines', [])
    engine_ids = {e['engine_id'] for e in engines}

    def parse_dep_string(dep_str):
        match = re.match(r"^([a-zA-Z0-9_-]+)(.*)$", dep_str)
        if not match:
            return dep_str
        return match.group(1)

    # Verify no missing dependencies
    for engine in engines:
        deps = engine.get('dependencies', [])
        for dep in deps:
            dep_name = parse_dep_string(dep)
            assert dep_name in engine_ids, f"Engine {engine['engine_id']} has missing dependency {dep_name}"

    # Cycle detection
    def has_cycle(node, visited, recursion_stack):
        visited.add(node)
        recursion_stack.add(node)

        # Get dependencies for node
        node_engine = next((e for e in engines if e['engine_id'] == node), None)
        if node_engine:
            for neighbor_str in node_engine.get('dependencies', []):
                neighbor = parse_dep_string(neighbor_str)
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, recursion_stack):
                        return True
                elif neighbor in recursion_stack:
                    return True

        recursion_stack.remove(node)
        return False

    for engine in engines:
        engine_id = engine['engine_id']
        assert not has_cycle(engine_id, set(), set()), f"Circular dependency detected involving {engine_id}"
