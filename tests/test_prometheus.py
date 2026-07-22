#!/usr/bin/env python3
import os
import sys
import json
import shutil
import unittest

# Dynamic sys.path insertion to circumvent hyphenated directory name import limits
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(root_dir, "openclaw-workspace", "prometheus"))

from prometheus_engine import PrometheusEngine

class TestPrometheusEngine(unittest.TestCase):
    def setUp(self):
        # Create a temporary workspace to test isolating PrometheusEngine
        self.test_workspace = "test_openclaw_workspace"
        self.engine = PrometheusEngine(workspace_path=self.test_workspace)

    def tearDown(self):
        # Clean up temporary test workspace
        test_workspace_dir = os.path.join(self.engine.root_path, self.test_workspace)
        if os.path.exists(test_workspace_dir):
            shutil.rmtree(test_workspace_dir)

    def test_run_audit_generates_documents(self):
        # Trigger the audit process
        stats = self.engine.run_audit()

        # Assert returns valid dictionary metrics
        self.assertIsInstance(stats, dict)
        self.assertIn("timestamp", stats)
        self.assertIn("checklist_count", stats)
        self.assertIn("test_file_count", stats)
        self.assertIn("unpinned_dependencies", stats)
        self.assertIn("uses_deprecated_openai", stats)

        # Check that files were created
        p_dir = os.path.join(self.engine.root_path, self.test_workspace, "prometheus")
        self.assertTrue(os.path.exists(p_dir))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "prometheus_summary.json")))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "capability_roadmap.md")))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "technical_debt_report.md")))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "bottleneck_report.md")))

        # Verify json summary contents
        with open(os.path.join(p_dir, "prometheus_summary.json"), "r") as jf:
            summary = json.load(jf)
            self.assertEqual(summary["timestamp"], stats["timestamp"])

if __name__ == "__main__":
    unittest.main()
