import unittest
import json
from app import app
from solomon_cognitive_architecture import SolomonCognitiveArchitecture
import app as flask_app

class TestCognitiveArchitecture(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        # Use memory DB for tests
        flask_app.cognitive_architecture = SolomonCognitiveArchitecture(':memory:')

    def test_learning_events_and_skills(self):
        # Post Learning Events
        res = self.client.post('/api/command-center/cognitive/learning-events', json={
            "content": "run npm install",
            "source": "terminal"
        })
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/api/command-center/cognitive/learning-events', json={
            "content": "deploy to render",
            "source": "terminal"
        })
        self.assertEqual(res.status_code, 200)

        # Test extraction
        res = self.client.post('/api/command-center/cognitive/advanced/extract-skills')
        data = json.loads(res.data)
        self.assertEqual(data["extracted_procedures"], 2)

    def test_graph_and_semantic_linking(self):
        # Post Node 1
        res = self.client.post('/api/command-center/cognitive/graph-nodes', json={
            "node_id": "n1",
            "node_type": "concept",
            "properties": {"name": "A"}
        })
        self.assertEqual(res.status_code, 200)

        # Post Node 2
        res = self.client.post('/api/command-center/cognitive/graph-nodes', json={
            "node_id": "n2",
            "node_type": "concept",
            "properties": {"name": "B"}
        })
        self.assertEqual(res.status_code, 200)

        # Trigger Semantic Link
        res = self.client.post('/api/command-center/cognitive/advanced/semantic-link')
        data = json.loads(res.data)
        self.assertEqual(data["new_edges_created"], 1)

    def test_curiosity_queue(self):
        res = self.client.post('/api/command-center/cognitive/advanced/curiosity-queue')
        self.assertEqual(res.status_code, 200)

    def test_get_meta_metrics(self):
        # Post a metric
        res = self.client.post('/api/command-center/cognitive/meta-metrics', json={
            "metric_name": "retrieval_speed",
            "metric_value": 42.5
        })
        self.assertEqual(res.status_code, 200)

        # Get metrics
        res = self.client.get('/api/command-center/cognitive/meta-metrics')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]['metric_name'], "retrieval_speed")

if __name__ == '__main__':
    unittest.main()
