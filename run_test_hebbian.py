import unittest
from solomon_unified_memory import UnifiedMemoryGraph

class TestHebbian(unittest.TestCase):
    def test_hebbian_learning(self):
        memory = UnifiedMemoryGraph()
        id1 = memory.ingest("Concept", "Machine learning")
        id2 = memory.ingest("Concept", "Deep learning")

        print("Recall results:", memory.recall("learning process"))

        for edge in memory.adjacency_list[id1]:
            print(f"Edge from {id1} to {edge.target_id}: {edge.relation_type}")

if __name__ == '__main__':
    unittest.main()
