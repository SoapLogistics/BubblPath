import logging
import random
from typing import Dict, Any

logger = logging.getLogger("SPLE_WorldModel")

class WorldModelSimulator:
    """
    Handles Part 1 of the SPLE blueprint: History of Learning Systems (specifically Model-Based RL).
    Maintains a simulated 'World Model' allowing the agent to 'dream' or simulate the outcomes
    of actions before executing them in reality.
    """
    def __init__(self):
        self.state_space = {"compute_load": 0.5, "memory_fragmentation": 0.2, "api_budget_remaining": 100.0}
        logger.info("World Model Simulator initialized for Model-Based RL.")

    def simulate_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates the state transition and expected reward of an action.
        """
        logger.info(f"Simulating action in World Model: {action}")

        predicted_state = self.state_space.copy()
        expected_reward = 0.0

        if action == "run_heavy_training_loop":
            predicted_state["compute_load"] = min(1.0, predicted_state["compute_load"] + 0.4)
            predicted_state["api_budget_remaining"] -= 10.0
            # Reward is high if budget allows, negative if it crashes the system
            expected_reward = 15.0 if predicted_state["api_budget_remaining"] > 0 else -50.0

        elif action == "trigger_sleep_consolidation":
            predicted_state["compute_load"] = max(0.1, predicted_state["compute_load"] - 0.3)
            predicted_state["memory_fragmentation"] = max(0.0, predicted_state["memory_fragmentation"] - 0.15)
            expected_reward = 5.0 # Steady, positive maintenance reward

        else:
             expected_reward = random.uniform(-1.0, 1.0)

        result = {
            "action_simulated": action,
            "predicted_next_state": predicted_state,
            "expected_reward": expected_reward,
            "is_safe": expected_reward > 0
        }

        logger.info(f"Simulation complete. Expected Reward: {expected_reward}, Safe: {result['is_safe']}")
        return result
