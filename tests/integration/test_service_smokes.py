import unittest
from backend.services.solomon_joe_bridge import get_status
from services.solomon_joe_bridge import queue_blueprint
from services.soss_workspace_status import get_workers

class TestServiceSmokes(unittest.TestCase):
    def test_backend_joe_bridge(self):
        self.assertEqual(get_status()["backend_stub"], True)

    def test_root_joe_bridge(self):
        res = queue_blueprint({"task": "test"})
        self.assertEqual(res["status"], "dry_run_generated")

    def test_soss_workspace(self):
        self.assertIn("Gabriel", get_workers())

    def test_system_events(self):
        from services.system_events import log_event, route_key
        self.assertEqual(route_key, "/api/internal/events")

    def test_truth_ledger(self):
        from services.truth_ledger import verify_truth
        self.assertTrue(verify_truth())

if __name__ == "__main__":
    unittest.main()
