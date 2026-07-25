"""
Ornstein-Uhlenbeck Exploration Engine (solomon_ou_exploration.py)
-----------------------------------------------------------------
Implements a mean-reverting stochastic process (Ornstein-Uhlenbeck).
Used by the Curiosity Director to explore continuous parameter spaces
smoothly, avoiding erratic random jumping while still allowing for
random discovery, gradually reverting to a baseline state.
"""

import random
import math
from typing import List

class OUExplorationEngine:
    def __init__(self, theta: float = 0.15, mu: float = 0.0, sigma: float = 0.2, dt: float = 1e-2, dim: int = 1):
        """
        theta: Rate of mean reversion
        mu: The mean/baseline to revert to
        sigma: Volatility / scale of the randomness
        dt: Time step
        dim: Dimensionality of the parameter space
        """
        self.theta = theta
        self.mu = mu
        self.sigma = sigma
        self.dt = dt
        self.dim = dim
        self.state = [self.mu] * self.dim
        # Local random instance for deterministic testing if needed
        self.rng = random.Random()

    def set_seed(self, seed: int):
        self.rng.seed(seed)

    def reset(self):
        self.state = [self.mu] * self.dim

    def step(self) -> List[float]:
        """
        Executes one step of the OU process.
        dx = theta * (mu - x) * dt + sigma * sqrt(dt) * N(0,1)
        """
        new_state = []
        for x in self.state:
            # Reversion term
            reversion = self.theta * (self.mu - x) * self.dt
            # Volatility (noise) term
            noise = self.sigma * math.sqrt(self.dt) * self.rng.gauss(0, 1)

            new_x = x + reversion + noise
            new_state.append(new_x)

        self.state = new_state
        return self.state
