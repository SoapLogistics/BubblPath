import unittest
from app import app
import json

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_benchmarking(self):
        response = self.client.post('/api/quantization/benchmarking', json={"model_id": "test_model"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["model_id"], "test_model")
        self.assertIn("ttft_ms", data["metrics"])

    def test_precision_ladder(self):
        response = self.client.post('/api/quantization/precision-ladder', json={"workload_type": "long_context"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["recommended_precision"], "KV4")

if __name__ == '__main__':
    unittest.main()
