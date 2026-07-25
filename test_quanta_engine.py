import unittest
from solomon_quanta_engine import QuantaEngine

class TestQuantaEngine(unittest.TestCase):
    def setUp(self):
        self.engine = QuantaEngine(threshold=0.2)

    def test_compression(self):
        dense = (0.5, 0.1, -0.3, -0.05, 0.9)
        ternary = self.engine.compress_to_ternary(dense)
        self.assertEqual(ternary, (1, 0, -1, 0, 1))

    def test_cosine_similarity(self):
        v1 = (1, 0, -1)
        v2 = (1, 0, -1)
        score = self.engine.cosine_similarity(v1, v2)
        self.assertAlmostEqual(score, 1.0)

        v3 = (-1, 0, 1)
        score_opp = self.engine.cosine_similarity(v1, v3)
        self.assertAlmostEqual(score_opp, -1.0)

        v4 = (1, 1, 1)
        score_orth = self.engine.cosine_similarity((1, -1, 0), v4)
        self.assertAlmostEqual(score_orth, 0.0)

    def test_routing(self):
        memory = [
            ("concept_a", (1, 1, 0, 0)),
            ("concept_b", (0, 0, -1, -1)),
            ("concept_c", (1, -1, 1, -1))
        ]

        state = (0.8, 0.9, 0.05, -0.1) # Compresses to (1, 1, 0, 0)
        compressed = self.engine.compress_to_ternary(state)
        best = self.engine.route_quantum_state(compressed, memory)

        self.assertEqual(best, "concept_a")

if __name__ == '__main__':
    unittest.main()
