import os
import importlib.util
import unittest

class TestServiceRegistry(unittest.TestCase):
    def test_service_classification(self):
        services_dir = "services"
        for filename in os.listdir(services_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(services_dir, filename)
                with open(filepath, "r") as f:
                    content = f.read()

                has_classification = any([
                    "route_key" in content,
                    "readiness_key" in content,
                    "internal_parent" in content,
                    "retired_reason" in content
                ])
                self.assertTrue(has_classification, f"{filename} missing classification")

if __name__ == "__main__":
    unittest.main()
