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

        # Ingest a node that will be forgotten (low importance, low access, no emotion)
        forgotten_id = self.memory.ingest("Failure", "Failed to compile the code.", importance=0.1)

        # Ingest a node that should move to Short-term (accessed multiple times)
        kept_id = self.memory.ingest("Skill", "Python programming", importance=0.8)
        self.memory.nodes[kept_id].access_count = 5

        # Flashbulb memory (high arousal, should resist decay even if not accessed)
        flashbulb_id = self.memory.ingest("Experience", "Server caught on fire", importance=0.5, valence=-0.9, arousal=0.9)

        # Give them some activation
        self.memory.nodes[forgotten_id].activation = 1.0
        self.memory.nodes[flashbulb_id].activation = 1.0

        # Consolidate decays activation
        self.memory.consolidate()

        # Flashbulb memory should have higher activation than forgotten memory due to arousal
        self.assertTrue(self.memory.nodes[flashbulb_id].activation > self.memory.nodes[forgotten_id].activation)

        # Wait for working_ttl to pass
        time.sleep(1.1)

        self.memory.consolidate()

        self.assertNotIn(forgotten_id, self.memory.nodes, "Low importance unaccessed node should be forgotten")
        self.assertIn(kept_id, self.memory.nodes, "Important/accessed node should be kept")
        self.assertEqual(self.memory.nodes[kept_id].layer, "Short-term", "Node should have moved to Short-term layer")

    def test_hebbian_learning(self):
        # Use disjoint words so they are not auto-linked initially
        id1 = self.memory.ingest("Concept", "Apple")
        id2 = self.memory.ingest("Concept", "Banana")

        # Initially, no direct hebbian link
        hebbian_linked = False
        for edge in self.memory.adjacency_list[id1]:
            if edge.target_id == id2 and edge.relation_type == "hebbian_association":
                hebbian_linked = True

        self.assertFalse(hebbian_linked, "Should not be linked initially")

        # Recall triggers hebbian learning because both are activated by the query
        self.memory.recall("Apple Banana")

        hebbian_linked = False
        for edge in self.memory.adjacency_list[id1]:
            if edge.target_id == id2 and edge.relation_type == "hebbian_association":
                hebbian_linked = True
                break

        self.assertTrue(hebbian_linked, "Should have created a hebbian association after co-activation")

    def test_dream_cycle(self):
        # Ingest a few nodes
        for i in range(5):
            self.memory.ingest("Random", f"Random fact number {i}")

        initial_edge_count = len(self.memory.edges)

        # Run dream cycle
        self.memory.dream_cycle(max_steps=5)

        # Dream cycle should potentially add edges or even new "Dream" synthesis nodes
        final_edge_count = len(self.memory.edges)
        self.assertTrue(final_edge_count >= initial_edge_count, "Dream cycle should have potentially added associations")

if __name__ == '__main__':
    unittest.main()
