import os
import json
import ast

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
