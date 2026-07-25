import unittest
import time
from solomon_unified_memory import UnifiedMemoryGraph

class TestUnifiedMemoryGraph(unittest.TestCase):
    def setUp(self):
        self.memory = UnifiedMemoryGraph()

    def test_ingest_and_recall(self):
        # Ingest nodes
        self.memory.ingest("Concept", "Machine learning involves training models on data.")
        self.memory.ingest("Concept", "Deep learning is a subset of machine learning using neural networks.")
        self.memory.ingest("Random", "The quick brown fox jumps over the lazy dog.")

        # Recall using related query
        results = self.memory.recall("neural networks and training")

        self.assertTrue(len(results) > 0)

        # The node with 'neural networks' or 'training' should have highest activation
        contents = [res['content'] for res in results]
        self.assertTrue(any("learning" in content for content in contents))

    def test_auto_linking(self):
        id1 = self.memory.ingest("Project", "Project Alpha uses Python and Flask")
        id2 = self.memory.ingest("Project", "Project Beta uses Python for data science")

        # Check if an edge was created between them due to 'Python'
        linked = False
        for edge in self.memory.adjacency_list[id2]:
            if edge.target_id == id1:
                linked = True
                break

        self.assertTrue(linked, "Nodes should be auto-linked based on shared words")

    def test_consolidation_and_forgetting(self):
        # Temporarily shorten TTLs for testing
        self.memory.working_ttl = 1
        self.memory.short_term_ttl = 2

        # Ingest a node that will be forgotten (low importance, low access)
        forgotten_id = self.memory.ingest("Failure", "Failed to compile the code.", importance=0.1)

        # Ingest a node that should move to Short-term (accessed multiple times)
        kept_id = self.memory.ingest("Skill", "Python programming", importance=0.8)
        self.memory.nodes[kept_id].access_count = 5

        # Wait for working_ttl to pass
        time.sleep(1.1)

        self.memory.consolidate()

        self.assertNotIn(forgotten_id, self.memory.nodes, "Low importance unaccessed node should be forgotten")
        self.assertIn(kept_id, self.memory.nodes, "Important/accessed node should be kept")
        self.assertEqual(self.memory.nodes[kept_id].layer, "Short-term", "Node should have moved to Short-term layer")

if __name__ == '__main__':
    unittest.main()
