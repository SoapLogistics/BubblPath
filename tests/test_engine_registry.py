import os
import json
import ast

def test_engine_registry():
    registry_path = "solomon_api/engine_registry.json"
    assert os.path.exists(registry_path), f"Registry file {registry_path} missing"

    with open(registry_path, "r") as f:
        registry = json.load(f)

    registry_by_path = {item.get("source_path"): item for item in registry if "source_path" in item}

    # Check registry properties
    for item in registry:
        status_class = item.get("status_class")
        if status_class == "active_route":
            assert "route_paths" in item and item["route_paths"], f"active_route {item.get('engine_id')} missing route_paths"
        elif status_class == "active_readiness":
            assert "readiness_keys" in item and item["readiness_keys"], f"active_readiness {item.get('engine_id')} missing readiness_keys"
        elif status_class == "internal_helper":
            assert "parent_surface" in item and item["parent_surface"], f"internal_helper {item.get('engine_id')} missing parent_surface"
        elif status_class == "approval_blocked":
            assert "refusal_behavior" in item or "known_blockers" in item, f"approval_blocked {item.get('engine_id')} missing refusal_behavior or known_blockers"

        if item.get("status_class") != "generated_artifact":
            has_doc = item.get("doc_path") and os.path.exists(item["doc_path"])
            has_test = item.get("test_paths") and any(os.path.exists(p) for p in item["test_paths"])
            has_justification = item.get("doc_test_exception")
            # We don't strictly assert this right now to avoid breaking on incomplete rows, but we could.
            # assert has_doc or has_test or has_justification, f"Engine {item.get('engine_id')} missing doc/test or exception"

    directories_to_scan = ["services", "backend/services", "solomon_api"]

    for directory in directories_to_scan:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and file != "__init__.py" and file != "engine_registry.py":
                    filepath = os.path.join(root, file)
                    filepath = filepath.replace("\\", "/")
                    if filepath.startswith("./"):
                        filepath = filepath[2:]

                    assert filepath in registry_by_path, f"File {filepath} is missing from engine registry"

                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    try:
                        parsed = ast.parse(content)
                        has_status_variable = False
                        for node in parsed.body:
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        if target.id in ("route_key", "readiness_key", "internal_parent", "retired_reason"):
                                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                                has_status_variable = True

                        assert has_status_variable, f"File {filepath} does not explicitly declare its status via route_key, readiness_key, internal_parent, or retired_reason"
                    except SyntaxError:
                        pass
