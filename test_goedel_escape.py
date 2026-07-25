import unittest
from solomon_goedel_escape import GoedelEscapeEngine

class TestGoedelEscape(unittest.TestCase):
    def setUp(self):
        self.engine = GoedelEscapeEngine(cycle_threshold=3)

    def test_loop_detection(self):
        state_a = {"task": "fix_bug", "strategy": "regex"}
        state_b = {"task": "fix_bug", "strategy": "parser"}

        # Step 1: A
        triggered, shift = self.engine.monitor_state(state_a)
        self.assertFalse(triggered)

        # Step 2: B
        triggered, shift = self.engine.monitor_state(state_b)
        self.assertFalse(triggered)

        # Step 3: A (2nd time)
        triggered, shift = self.engine.monitor_state(state_a)
        self.assertFalse(triggered)

        # Step 4: A (3rd time, hits threshold)
        triggered, shift = self.engine.monitor_state(state_a)
        self.assertTrue(triggered)
        self.assertTrue("GÖDEL ESCAPE" in shift)

        # History should be cleared after trigger
        self.assertEqual(len(self.engine.state_history), 0)

if __name__ == '__main__':
    unittest.main()
