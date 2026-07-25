import math
from functools import lru_cache
from typing import Tuple

class LokiQuantEngine:
    """
    Ultra-efficient quantitative finance models.
    Uses lru_cache for memoization of complex math to maximize calculation speed per tick.
    """

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Approximation of the Cumulative Distribution Function for standard normal distribution."""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    @staticmethod
    @lru_cache(maxsize=1024)
    def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculates European Call Option price using Black-Scholes.
        S: Spot price, K: Strike price, T: Time to maturity (years), r: Risk-free rate, sigma: Volatility.
        """
        if T <= 0.0:
            return max(0.0, S - K)

        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        return S * LokiQuantEngine._norm_cdf(d1) - K * math.exp(-r * T) * LokiQuantEngine._norm_cdf(d2)

    @staticmethod
    def ornstein_uhlenbeck_next_step(current_price: float, long_term_mean: float, mean_reversion_speed: float, volatility: float, dt: float, random_shock: float) -> float:
        """
        Simulates one step of an Ornstein-Uhlenbeck process (mean-reverting).
        Extremely fast calculation for high-frequency pairs-trading simulation.
        """
        drift = mean_reversion_speed * (long_term_mean - current_price) * dt
        diffusion = volatility * math.sqrt(dt) * random_shock
        return current_price + drift + diffusion
