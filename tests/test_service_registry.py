import os
import glob
import ast

def test_service_registry_classification():
    services_dir = "services"
    if not os.path.exists(services_dir):
        return

    for py_file in glob.glob(os.path.join(services_dir, "*.py")):
        if py_file.endswith("__init__.py"):
            continue

        with open(py_file, "r") as f:
            content = f.read()

        tree = ast.parse(content)

        has_classification = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id in ["route_key", "readiness_key", "internal_parent", "retired_reason"]:
                                    has_classification = True

        assert has_classification, f"Module {py_file} is missing classification (route_key, readiness_key, etc.)"
