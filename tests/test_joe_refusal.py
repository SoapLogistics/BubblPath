import unittest
from services.solomon_joe_bridge import queue_blueprint

class TestJoeRefusal(unittest.TestCase):
    def test_refusal_without_approval(self):
        res = queue_blueprint({"execute": True, "approval": False})
        self.assertEqual(res["status"], "dry_run_generated")

if __name__ == "__main__":
    unittest.main()
