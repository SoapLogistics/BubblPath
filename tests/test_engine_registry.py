import os
import json
import unittest

class TestEngineRegistry(unittest.TestCase):
    def test_engine_registry_exists(self):
        self.assertTrue(os.path.exists("solomon_api/engine_registry.json"))
        self.assertTrue(os.path.exists("docs/solomon_engine_registry.md"))

    def test_no_anonymous_engines(self):
        with open("solomon_api/engine_registry.json", "r") as f:
            registry = json.load(f)

        registered_files = []
        exclusions = []

        if isinstance(registry, dict):
            engines = registry.get("engines", [])
            exclusions = registry.get("exclusions", [])
        elif isinstance(registry, list):
            engines = registry
        else:
            self.fail("Engine registry must be a list or a dict")

        for engine in engines:
            self.assertIn("status_class", engine)
            self.assertIn("owner_family", engine)
            self.assertIn("route_paths", engine)
            if "file_path" in engine:
                registered_files.append(engine["file_path"].replace('\\', '/'))

        # Check all python files in target directories
        target_dirs = ["services", "backend/services", "solomon_api"]
        for target_dir in target_dirs:
            if not os.path.exists(target_dir):
                continue
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file).replace('\\', '/')
                        if file_path in exclusions:
                            continue

                        # Only in services/ check for module-level variables
                        if root == "services":
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()

                            has_route_key = "route_key" in content
                            has_readiness_key = "readiness_key" in content
                            has_internal_parent = "internal_parent" in content
                            has_retired_reason = "retired_reason" in content

                            self.assertTrue(
                                has_route_key or has_readiness_key or has_internal_parent or has_retired_reason,
                                f"File {file_path} in services/ must declare route_key, readiness_key, internal_parent, or retired_reason"
                            )

                        self.assertTrue(
                            file_path in registered_files or len(engines) == 0,
                            f"File {file_path} must be registered in solomon_api/engine_registry.json"
                        )

if __name__ == '__main__':
    unittest.main()
