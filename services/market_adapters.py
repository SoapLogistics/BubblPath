
from typing import Dict, Any, List
import hashlib

internal_parent = "futures_engine"
route_key = "market_adapters"
from typing import Dict, Any, List
import hashlib


class PolymarketAdapter(object):
    name = "polymarket"
    version = "1.0.0"

    def build_scenario(self, candidate: Any) -> Dict[str, Any]:
        """
        In a true live system, this would fetch the live orderbook.
        Here we structure the API ingestion schema.
        """
        # Ensure we have the base live odds or features provided
        live_implied_prob = candidate.features.get("live_implied_prob", 0.5)
        liquidity_discount = candidate.features.get("liquidity_discount", 0.0)

        return {
            "base_prob": max(0.01, live_implied_prob - liquidity_discount),
            "market_type": "binary_prediction"
        }

    def simulate_trial(self, scenario: Dict[str, Any], rng_seed: int) -> bool:
        # Pseudo-random trial based on base probability
        hash_val = int(hashlib.md5(f"poly_{rng_seed}".encode()).hexdigest(), 16)
        return (hash_val % 10000) / 10000.0 < scenario["base_prob"]

    def sensitivity_variants(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Stress test the probability against sudden line movement
        base = scenario["base_prob"]
        return [
            {"base_prob": base * 0.90}, # -10% severe line shift
            {"base_prob": base * 0.95}  # -5% standard line shift
        ]

class DraftKingsAdapter(object):
    name = "draftkings"
    version = "1.0.0"

    def build_scenario(self, candidate: Any) -> Dict[str, Any]:
        # Sports prop bet modeling
        historical_cover_rate = candidate.features.get("historical_cover_rate", 0.5)
        injuries_factor = candidate.features.get("injuries_factor", 1.0)

        return {
            "base_prob": min(0.99, historical_cover_rate * injuries_factor),
            "bet_type": "prop_boost"
        }

    def simulate_trial(self, scenario: Dict[str, Any], rng_seed: int) -> bool:
        hash_val = int(hashlib.md5(f"dk_{rng_seed}".encode()).hexdigest(), 16)
        return (hash_val % 10000) / 10000.0 < scenario["base_prob"]

    def sensitivity_variants(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        base = scenario["base_prob"]
        return [
            {"base_prob": base * 0.92}, # Injury downgrade variant
            {"base_prob": base * 0.88}  # Key player ruled out
        ]

class KalshiAdapter(object):
    name = "kalshi"
    version = "1.0.0"

    def build_scenario(self, candidate: Any) -> Dict[str, Any]:
        # Macro-economic/Event futures modeling
        return {
            "base_prob": candidate.features.get("economic_indicator_prob", 0.5)
        }

    def simulate_trial(self, scenario: Dict[str, Any], rng_seed: int) -> bool:
        hash_val = int(hashlib.md5(f"kalshi_{rng_seed}".encode()).hexdigest(), 16)
        return (hash_val % 10000) / 10000.0 < scenario["base_prob"]

    def sensitivity_variants(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        base = scenario["base_prob"]
        return [
            {"base_prob": base * 0.85}, # High volatility macro shock
        ]
