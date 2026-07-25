import unittest
from solomon_abstract_reasoning import FractalOntologySynthesizer

class TestFractalOntology(unittest.TestCase):
    def setUp(self):
        self.synth = FractalOntologySynthesizer()

        # Simple 2D semantic space
        # Physics Domain
        self.synth.add_domain_concept("physics", "velocity", (2.0, 0.0))
        self.synth.add_domain_concept("physics", "mass", (0.0, 2.0))
        self.synth.add_domain_concept("physics", "momentum", (2.0, 2.0))

        # Finance Domain (shifted by +5, +5)
        self.synth.add_domain_concept("finance", "cash_flow", (7.0, 5.0))
        self.synth.add_domain_concept("finance", "capital", (5.0, 7.0))
        self.synth.add_domain_concept("finance", "market_momentum", (7.0, 7.0))

    def test_centroid_calculation(self):
        c = self.synth.calculate_centroid("physics")
        self.assertAlmostEqual(c[0], (2.0 + 0.0 + 2.0) / 3)
        self.assertAlmostEqual(c[1], (0.0 + 2.0 + 2.0) / 3)

    def test_capability_leap(self):
        # We take a physics concept (velocity) and leap it to finance
        result = self.synth.synthesize_capability_leap("physics", "finance", (2.0, 0.0))
        self.assertIsNotNone(result)

        # Shift should be (5, 5). So (2,0) + (5,5) = (7,5) -> should map exactly to cash_flow
        self.assertEqual(result["closest_grounded_concept"], "cash_flow")
        self.assertAlmostEqual(result["distance"], 0.0)

if __name__ == '__main__':
    unittest.main()
