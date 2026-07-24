import unittest
from app import app
import json

class Test50Step(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_50_step_optimize(self):
        response = self.client.post('/api/quantization/50-step-optimize', json={"model_id": "test_model"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["model_id"], "test_model")
        self.assertEqual(data["pipeline_status"], "success")
        self.assertEqual(data["optimizations_applied"], 50)
        self.assertIn("Step 1", data["results"])
        self.assertIn("Step 50", data["results"])

if __name__ == '__main__':
    unittest.main()
