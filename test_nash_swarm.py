import unittest
from solomon_nash_swarm import Agent, NashSwarmNegotiator

class TestNashSwarm(unittest.TestCase):
    def test_nash_bargaining_solution(self):
        outcomes = ["plan_A", "plan_B", "plan_C"]

        # Agent 1 loves A, likes B, hates C
        a1 = Agent("worker_1", {"plan_A": 10.0, "plan_B": 5.0, "plan_C": 0.0})
        # Agent 2 hates A, likes B, loves C
        a2 = Agent("worker_2", {"plan_A": 0.0, "plan_B": 5.0, "plan_C": 10.0})
        # Agent 3 thinks B is best for the swarm overall
        a3 = Agent("worker_3", {"plan_A": 2.0, "plan_B": 8.0, "plan_C": 2.0})

        negotiator = NashSwarmNegotiator([a1, a2, a3], outcomes)
        result = negotiator.resolve_contention()

        self.assertTrue(result["success"])
        # plan_A product: 10 * 0 * 2 = 0
        # plan_B product: 5 * 5 * 8 = 200
        # plan_C product: 0 * 10 * 2 = 0
        # Therefore, B is the Nash Bargaining Solution
        self.assertEqual(result["consensus_outcome"], "plan_B")
        self.assertEqual(result["nash_product_score"], 200.0)

    def test_no_equilibrium(self):
        outcomes = ["plan_A", "plan_B"]
        a1 = Agent("w1", {"plan_A": 10.0, "plan_B": 0.0})
        a2 = Agent("w2", {"plan_A": 0.0, "plan_B": 10.0})

        negotiator = NashSwarmNegotiator([a1, a2], outcomes)
        result = negotiator.resolve_contention()

        self.assertFalse(result["success"])
        self.assertEqual(result["consensus_outcome"], "no_equilibrium_found")

if __name__ == '__main__':
    unittest.main()
