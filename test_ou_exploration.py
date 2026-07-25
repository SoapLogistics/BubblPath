import unittest
from solomon_ou_exploration import OUExplorationEngine

class TestOUExploration(unittest.TestCase):
    def setUp(self):
        self.engine = OUExplorationEngine(theta=0.15, mu=0.0, sigma=0.2, dt=1.0, dim=1)
        self.engine.set_seed(42) # Ensure deterministic test

    def test_ou_step(self):
        # Initial state is [0.0]
        step1 = self.engine.step()
        self.assertEqual(len(step1), 1)
        self.assertNotEqual(step1[0], 0.0) # Should have moved due to noise

        # Test mean reversion logic
        # If we manually set state extremely high, the reversion term should pull it down
        self.engine.state = [10.0]
        step2 = self.engine.step()
        # It should move downwards (theta * (0 - 10) * 1.0 = -1.5 reversion)
        self.assertTrue(step2[0] < 10.0)

        # If we set it extremely low, it should pull it up
        self.engine.state = [-10.0]
        step3 = self.engine.step()
        self.assertTrue(step3[0] > -10.0)

if __name__ == '__main__':
    unittest.main()
