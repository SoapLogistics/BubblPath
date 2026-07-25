import unittest
import time
import os
from solomon_quantized_memory import QuantizedBrainMap, LAYER_SHORT_TERM

class TestQuantizedMemory(unittest.TestCase):
    def setUp(self):
        self.memory = QuantizedBrainMap(max_nodes=100)
        if os.path.exists("solomon_brain_map.bin"):
            os.remove("solomon_brain_map.bin")

    def tearDown(self):
        self.memory.stop_ans()
        if os.path.exists("solomon_brain_map.bin"):
            os.remove("solomon_brain_map.bin")

    def test_amygdala_reflex(self):
        id1 = self.memory.ingest("Concept", "Calm lake")
        id2 = self.memory.ingest("Experience", "Tiger attack", arousal=0.9, valence=-0.9)

        # Test routing bypasses normal graph (L0 cache hit)
        results = self.memory.recall("danger tiger fire")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], id2)

    def test_vectorized_hebbian(self):
        id1 = self.memory.ingest("Concept", "Machine")
        id2 = self.memory.ingest("Concept", "Learning")

        # Manually link with tiny weight to test SpMV spreading
        idx1 = self.memory.id_map[id1]
        idx2 = self.memory.id_map[id2]
        self.memory.adj_matrix[idx1, idx2] = 0.5
        self.memory.is_matrix_dirty = True

        self.memory.recall("Machine Learning")

        # Hebbian delta should have strengthened it
        new_weight = self.memory.adj_matrix[idx1, idx2]
        self.assertTrue(new_weight > 0.5)

    def test_synaptic_scaling_and_binary_serialization(self):
        id1 = self.memory.ingest("Temp", "Temporary thought")
        idx1 = self.memory.id_map[id1]

        # Fake age for serialization to Long Term
        self.memory.nodes[idx1].creation_time = time.time() - 90000
        self.memory.nodes[idx1].layer = LAYER_SHORT_TERM

        self.memory.consolidate()

        # Should be removed from L1 RAM
        self.assertNotIn(idx1, self.memory.nodes)

        # Should be written to binary blob
        self.assertTrue(os.path.exists("solomon_brain_map.bin"))
        self.assertTrue(os.path.getsize("solomon_brain_map.bin") > 0)

if __name__ == '__main__':
    unittest.main()
