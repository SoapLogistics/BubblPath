import unittest
from app import app
import json

class TestChronosAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_simulate(self):
        payload = {
            "start_state": {"at_home": True},
            "goal_state": {"at_store": True},
            "actions": [
                {"name": "goto_store", "cost": 1.0, "preconditions": {"at_home": True}, "effects": {"at_store": True}}
            ]
        }
        resp = self.app.post('/api/chronos/simulate', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['final_state']['at_store'], True)

if __name__ == '__main__':
    unittest.main()
