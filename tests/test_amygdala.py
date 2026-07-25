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

    def test_dream_consolidation_pruning(self):
        import time

        # Add a "weak" memory (age is old, hits < 3)
        self.router._reflex_arc["weak_hash"] = {
            "response": "weak response",
            "hit_count": 1,
            "last_accessed": time.time() - 90000 # Older than max_age (86400)
        }

        # Add a "strong" memory (age is old, but hits >= 3)
        self.router._reflex_arc["strong_hash"] = {
            "response": "strong response",
            "hit_count": 10,
            "last_accessed": time.time() - 90000
        }

        # Add a "new" memory (hits low, but recent)
        self.router._reflex_arc["new_hash"] = {
            "response": "new response",
            "hit_count": 1,
            "last_accessed": time.time() - 100
        }

        # Run dream consolidation
        pruned = self.router.dream_consolidation()

        # It should prune exactly 1 memory (the weak one)
        self.assertEqual(pruned, 1)
        self.assertNotIn("weak_hash", self.router._reflex_arc)
        self.assertIn("strong_hash", self.router._reflex_arc)
        self.assertIn("new_hash", self.router._reflex_arc)

    def test_dream_consolidation_capacity(self):
        import time
        # Flood the reflex arc with 110 items (capacity is 100)
        for i in range(110):
            # i=0 to i=9 are the weakest (lowest hits)
            self.router._reflex_arc[f"hash_{i}"] = {
                "response": "spam",
                "hit_count": i, # Higher i = higher score
                "last_accessed": time.time()
            }

        pruned = self.router.dream_consolidation(max_capacity=100)

        # It should prune exactly 10 items to get down to max_capacity
        self.assertEqual(pruned, 10)
        self.assertEqual(len(self.router._reflex_arc), 100)

        # Because we prune the weakest scores (lowest hits), hash_0 to hash_9 should be gone
        self.assertNotIn("hash_0", self.router._reflex_arc)
        self.assertNotIn("hash_9", self.router._reflex_arc)
        # hash_109 (highest hits) should definitely still be there
        self.assertIn("hash_109", self.router._reflex_arc)


if __name__ == '__main__':
    unittest.main()
