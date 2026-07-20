import os
import sys
import json
import unittest
import shutil
import tempfile

# Add the hyphenated workspace directory to sys.path so we can import prometheus cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "openclaw-workspace")))
from prometheus.prometheus_engine import PrometheusEngine

class TestPrometheusEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Create a mock repo structure
        self.workspace_dir = os.path.join(self.temp_dir, "openclaw-workspace")
        self.prometheus_dir = os.path.join(self.workspace_dir, "prometheus")
        os.makedirs(self.prometheus_dir)

        # Create a mock __init__.py python file
        self.init_file = os.path.join(self.temp_dir, "__init__.py")
        with open(self.init_file, "w") as f:
            f.write("# TODO: Implement sub-modules\n")

        # Create a mock app.py with routes and TODOs
        self.app_file = os.path.join(self.temp_dir, "app.py")
        with open(self.app_file, "w") as f:
            f.write(
                "@app.route(\"/api/health\")\n"
                "def health():\n"
                "    # FIXME: add uptime\n"
                "    pass\n"
            )

        self.engine = PrometheusEngine(repo_root=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_scan_and_generate_reports(self):
        # 1. Run codebase scan
        results = self.engine.scan_codebase()
        self.assertEqual(results["file_count"], 2)

        # Should detect one TODO and one FIXME
        todos = [t["text"] for t in results["todos"]]
        self.assertTrue(any("TODO" in t for t in todos))
        self.assertTrue(any("FIXME" in t for t in todos))

        # Should detect /api/health route
        routes = [ep["route"] for ep in results["endpoints"]]
        self.assertEqual(routes, ["/api/health"])

        # 2. Run engine cycle to generate physical output reports
        cycle_results = self.engine.run_engine_cycle()
        self.assertEqual(cycle_results["file_count"], 2)

        # Verify physical files exist in temp directory
        self.assertTrue(os.path.exists(os.path.join(self.prometheus_dir, "capability_map.json")))
        self.assertTrue(os.path.exists(os.path.join(self.prometheus_dir, "architecture_drift_report.md")))
        self.assertTrue(os.path.exists(os.path.join(self.prometheus_dir, "technical_debt_report.md")))

        # Verify JSON capability content
        with open(os.path.join(self.prometheus_dir, "capability_map.json"), "r") as f:
            cap_data = json.load(f)
        self.assertEqual(cap_data["telemetry"]["total_monitored_source_files"], 2)
        self.assertEqual(cap_data["telemetry"]["exposed_secure_endpoints_count"], 1)

if __name__ == "__main__":
    unittest.main()
