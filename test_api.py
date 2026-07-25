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

    def test_tda_analyze(self):
        payload = {
            "points": [[0,0], [1,0], [0,1], [1,1], [5,5]],
            "epsilon": 1.1
        }
        resp = self.app.post('/api/sple/tda/analyze', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['topology']['clusters_b0'], 2)

    def test_goedel_monitor(self):
        payload = {"state": {"looping": True}}
        # Trigger 3 times to hit threshold
        self.app.post('/api/sple/goedel/monitor', json=payload)
        self.app.post('/api/sple/goedel/monitor', json=payload)
        resp = self.app.post('/api/sple/goedel/monitor', json=payload)
        data = json.loads(resp.data)
        self.assertTrue(data['triggered'])

    def test_ou_step(self):
        payload = {"reset": True}
        resp = self.app.post('/api/sple/ou-exploration/step', json=payload)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['state']), 1)

    def test_harden_250(self):
        resp = self.app.post('/api/system/harden-250', json={})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['report']['total_tasks_run'], 250)
        self.assertEqual(data['report']['successful_tasks'], 250)

if __name__ == '__main__':
    unittest.main()
