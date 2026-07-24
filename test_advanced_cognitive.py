import unittest
import json
from app import app
from solomon_cognitive_architecture import SolomonCognitiveArchitecture
import app as flask_app

class TestAdvancedCognitiveArchitecture(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        flask_app.cognitive_architecture = SolomonCognitiveArchitecture(':memory:')

    def test_classify_and_report(self):
        # Post facts
        self.client.post('/api/command-center/cognitive/learning-events', json={
            "content": "Solomon is an AI.",
            "source": "manual"
        })
        self.client.post('/api/command-center/cognitive/learning-events', json={
            "content": "run npm start",
            "source": "terminal"
        })

        # Classify
        res = self.client.post('/api/command-center/cognitive/advanced/classify-memories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["classified_memories"], 1) # only "run npm start" is a proc

        # Report
        res = self.client.get('/api/command-center/cognitive/advanced/learning-report')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["active_memories"], 2)
        self.assertEqual(data["procedural_memories"], 1)

    def test_detect_opportunities(self):
        flask_app.cognitive_architecture.autonomous_growth.record_observation("worker", "code_execution", "Process timed out after 30s")
        flask_app.cognitive_architecture.autonomous_growth.record_observation("worker", "code_execution", "Process success")

        res = self.client.post('/api/command-center/cognitive/advanced/detect-opportunities')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["opportunities_detected"], 1)

    def test_repair_graph(self):
        flask_app.cognitive_architecture.add_graph_node("orphan_1", "concept")

        res = self.client.post('/api/command-center/cognitive/advanced/repair-graph')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["orphans_repaired"], 1)

    def test_optimize_learning(self):
        flask_app.cognitive_architecture.log_meta_metric("retrieval_accuracy", 0.75)
        flask_app.cognitive_architecture.log_meta_metric("retrieval_accuracy", 0.70)

        res = self.client.post('/api/command-center/cognitive/advanced/optimize-learning')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["new_chunk_size"], 256)

if __name__ == '__main__':
    unittest.main()
