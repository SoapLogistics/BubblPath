"""
Nash Equilibrium Swarm Negotiation (solomon_nash_swarm.py)
----------------------------------------------------------
Implements a negotiation protocol for Gabriel worker agents.
Workers resolve resource contention or consensus by finding a Nash Equilibrium
where no agent can unilaterally improve their payoff without harming the swarm's global utility.
"""

from typing import List, Dict, Tuple, Any

class Agent:
    def __init__(self, name: str, preferences: Dict[str, float]):
        self.name = name
        self.preferences = preferences # Mapping of outcome_id -> payoff (utility)
        self.current_proposal = None

class NashSwarmNegotiator:
    def __init__(self, agents: List[Agent], possible_outcomes: List[str]):
        self.agents = agents
        self.outcomes = possible_outcomes

    def evaluate_payoff(self, agent: Agent, outcome: str) -> float:
        """Returns the specific utility payoff for an agent given an outcome."""
        return agent.preferences.get(outcome, 0.0)

    def find_pure_nash_equilibrium(self) -> Tuple[bool, str, float]:
        """
        In a cooperative swarm setting, we simplify finding the equilibrium by looking for
        the outcome that maximizes the product of all agents' utilities (Nash Bargaining Solution),
        ensuring fairness and Pareto efficiency.

        Returns:
            Tuple of (Success_Boolean, Best_Outcome_ID, Max_Nash_Product)
        """
        best_outcome = None
        max_nash_product = -1.0

        for outcome in self.outcomes:
            nash_product = 1.0
            valid = True

            for agent in self.agents:
                payoff = self.evaluate_payoff(agent, outcome)
                if payoff <= 0:
                    # If any agent strongly rejects (0 or negative utility), it breaks the cooperative product
                    valid = False
                    break
                nash_product *= payoff

            if valid and nash_product > max_nash_product:
                max_nash_product = nash_product
                best_outcome = outcome

        if best_outcome:
            return True, best_outcome, max_nash_product
        else:
            return False, "no_equilibrium_found", 0.0

    def resolve_contention(self) -> Dict[str, Any]:
        """Runs the negotiation and returns the consensus state."""
        success, best_outcome, score = self.find_pure_nash_equilibrium()

        return {
            "success": success,
            "consensus_outcome": best_outcome,
            "nash_product_score": score,
            "agent_payoffs": {
                agent.name: self.evaluate_payoff(agent, best_outcome) for agent in self.agents
            } if success else {}
        }
