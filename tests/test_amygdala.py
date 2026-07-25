import unittest
from solomon_core.gabriel.amygdala import AmygdalaRouter

class TestAmygdalaRouter(unittest.TestCase):

    def setUp(self):
        self.router = AmygdalaRouter()

    def test_quantization(self):
        # Ensure normalization and hashing are consistent
        hash1 = self.router._quantize("Hello World!")
        hash2 = self.router._quantize("hello  world  ")
        self.assertEqual(hash1, hash2)

    def test_analyze_tags(self):
        tags = self.router.analyze_tags("Hurry up, this is an urgent emergency!")
        self.assertGreater(tags["urgency"], 0)
        self.assertEqual(tags["frustration"], 0)

        tags2 = self.router.analyze_tags("This stupid broken code makes me angry.")
        self.assertGreater(tags2["frustration"], 0)

        tags3 = self.router.analyze_tags("Please explain and analyze the architecture.")
        self.assertGreater(tags3["complexity"], 0)

    def test_myelination_and_reflex(self):
        # A simple greeting
        msg = "hi there"

        # Initially, it's novel and not in the reflex arc
        decision1 = self.router.process(msg)
        self.assertEqual(decision1["route"], "cortex")
        self.assertEqual(decision1["tags"]["novelty"], 1.0)

        # Cortex processes it and we learn it
        learned = self.router.learn(msg, "Hello! How can I help?")
        self.assertTrue(learned)

        # Second time, it should be a reflex
        decision2 = self.router.process(msg)
        self.assertEqual(decision2["route"], "reflex")
        self.assertEqual(decision2["response"], "Hello! How can I help?")
        self.assertEqual(decision2["tags"]["novelty"], 0.0)

    def test_complex_not_learned_by_default(self):
        # A complex query
        msg = "Please analyze the architecture and explain the design."

        decision1 = self.router.process(msg)
        self.assertEqual(decision1["route"], "cortex")

        # Try to learn it
        learned = self.router.learn(msg, "Here is an analysis...")

        # Because complexity is high, it shouldn't learn by default
        self.assertFalse(learned)

        # It still routes to cortex
        decision2 = self.router.process(msg)
        self.assertEqual(decision2["route"], "cortex")

if __name__ == '__main__':
    unittest.main()
