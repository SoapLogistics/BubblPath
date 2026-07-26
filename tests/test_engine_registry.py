import os
import json

def test_engine_registry():
    registry_path = "solomon_api/engine_registry.json"
    assert os.path.exists(registry_path)
    with open(registry_path, "r") as f:
        registry = json.load(f)
    assert isinstance(registry, list)

    # Check services/ python files
    services_dir = "services"
    if os.path.exists(services_dir):
        for root, _, files in os.walk(services_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    filepath = os.path.join(root, file)
                    with open(filepath, "r") as f:
                        content = f.read()
                    assert any(key in content for key in ["route_key", "readiness_key", "internal_parent", "retired_reason"])
