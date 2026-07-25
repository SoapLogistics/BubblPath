import logging
import random
from typing import Dict, Any

logger = logging.getLogger("SPLE_OU_Exploration")

class OrnsteinUhlenbeckExplorer:
    """
    Step 79 of the Awesomeness Plan: Ornstein-Uhlenbeck Exploration.
    Adds mean-reverting noise to the curiosity engine's exploration trajectory.
    This prevents the AI from getting stuck in "rabbit holes" (local minima) by
    gently pulling it back towards the global mean of its knowledge map over time.
    """
    def __init__(self, theta: float = 0.15, mu: float = 0.0, sigma: float = 0.2):
        self.theta = theta # Rate of mean reversion
        self.mu = mu       # Long-term mean (center of knowledge base)
        self.sigma = sigma # Volatility (exploration randomness)
        self.current_state = 0.0 # Current distance from center
        logger.info("Ornstein-Uhlenbeck Explorer initialized.")

    def step_exploration(self) -> Dict[str, Any]:
        """
        Calculates the next step in the exploration trajectory using the O-U process.
        Formula: dx = theta * (mu - x) * dt + sigma * dW
        """
        # dt = 1.0, dW (Wiener process) simulated by Gaussian noise
        dW = random.gauss(0, 1)

        drift = self.theta * (self.mu - self.current_state)
        diffusion = self.sigma * dW

        step_change = drift + diffusion
        self.current_state += step_change

        logger.debug(f"O-U Step: Drift={drift:.3f}, Diffusion={diffusion:.3f}, New State={self.current_state:.3f}")

        # Interpret the state:
        # Close to 0 -> Exploit known concepts.
        # Far from 0 -> Explore radical new concepts.
        action = "Exploit known domain" if abs(self.current_state) < 0.5 else "Explore radical paradigm"

        return {
            "ou_state_value": round(self.current_state, 4),
            "drift_pull": round(drift, 4),
            "noise_push": round(diffusion, 4),
            "exploration_action": action
        }
