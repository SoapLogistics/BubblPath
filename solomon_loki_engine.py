"""
Solomon Perpetual Learning Machine
Project Loki: Sports Intelligence Engine

This module implements:
1. Shin's Probability Solver: A binary numerical search model to neutralize bookmaker
   overround ("vig" or "juice") and extract mathematically calibrated true probabilities.
2. Fractional Kelly Criterion: Risk-adjusted fractional bankroll staking optimizer to prevent ruin.
"""

import math
from typing import List, Dict, Any, Tuple

class LokiIntelligenceEngine:
    """
    Project Loki's sports betting and odds evaluation engine.
    Calculates true implied probabilities and risk-adjusted bankroll stakes.
    """

    @classmethod
    def solve_shin_probabilities(cls, implied_probabilities: List[float], max_iterations: int = 100, tolerance: float = 1e-6) -> Tuple[float, List[float]]:
        """
        Solves for Shin's parameter 'z' (informed bettor fraction) and the true
        probabilities 'p_i' using a binary numerical search such that sum(p_i) = 1.0.

        Shin's formulation:
            pi_i = (1 - z) * p_i + z * sqrt(p_i)
        We solve for p_i given pi_i:
            p_i = (sqrt(z^2 + 4 * (1 - z) * pi_i) - z) / (2 * (1 - z))
        """
        n = len(implied_probabilities)
        if n == 0:
            return 0.0, []

        # Implied probabilities might sum to > 1.0 (containing the vig)
        sum_implied = sum(implied_probabilities)

        # Binary search bounds for z
        low_z = 0.0
        high_z = 1.0 - 1e-9
        z = 0.0

        true_probabilities = [0.0] * n

        for _ in range(max_iterations):
            z = (low_z + high_z) / 2.0

            # Compute true probabilities for current z
            sum_p = 0.0
            for i in range(n):
                pi = implied_probabilities[i]
                numerator = math.sqrt(z**2 + 4.0 * (1.0 - z) * pi) - z
                denominator = 2.0 * (1.0 - z)
                if denominator < 1e-9:
                    p = pi
                else:
                    p = (numerator / denominator) ** 2
                true_probabilities[i] = p
                sum_p += p

            # Adjust bounds
            if abs(sum_p - 1.0) < tolerance:
                break
            elif sum_p > 1.0:
                # If sum_p is too high, z must be larger to compress true probabilities more
                low_z = z
            else:
                high_z = z

        # Final normalization to handle micro-residuals
        total_p = sum(true_probabilities)
        if total_p > 0:
            true_probabilities = [p / total_p for p in true_probabilities]

        return float(round(z, 4)), [float(round(p, 4)) for p in true_probabilities]

    @classmethod
    def calculate_kelly_stake(
        cls,
        true_probability: float,
        decimal_odds: float,
        fraction: float = 0.25 # Quarter-Kelly default
    ) -> float:
        """
        Calculates optimal bankroll stake size using Fractional Kelly Criterion.
        Formula:
            f = fraction * (p * b - (1 - p)) / b
        where:
            b = decimal_odds - 1.0 (net profit multiplier)
            p = true_probability
        """
        if decimal_odds <= 1.0:
            return 0.0

        b = decimal_odds - 1.0
        p = true_probability

        # Standard Kelly formula
        f_star = (p * b - (1.0 - p)) / b

        # Apply conservative scaling fraction
        fractional_stake = fraction * f_star

        # Clip negative stakes (no bet / hedge condition)
        return float(round(max(0.0, fractional_stake), 4))
