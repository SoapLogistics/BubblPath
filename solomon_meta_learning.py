"""
Solomon Perpetual Learning Machine
Phase 12: Learning How to Learn (Meta-Learning)

Assesses learning performance history and optimizes the learning algorithms themselves
by dynamically modifying coefficients in the Opportunity Weighting Matrix and Wisdom Gate filters.
"""

from typing import Dict, Any, List
from solomon_mnemosyne_db import SolomonMnemosyneDB

class MetaLearningEngine:
    """
    Autonomously optimizes Solomon's learning and safety decision algorithms.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def optimize_learning_algorithms(self, execution_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingests a history of previous experiment runs and calibrates the coefficients
        of the Curiosity Engine and Wisdom Layer to maximize learning rate efficiency.
        """
        # Baseline Curiosity matrix weights
        curiosity_weights = {
            "w_v": 0.40,  # Value
            "w_d": 0.20,  # Difficulty
            "w_u": 0.30,  # Future Use
            "w_r": 0.20,  # Risk
            "w_c": 0.10   # Compute Cost
        }

        # Baseline Wisdom matrix weights
        wisdom_weights = {
            "w_confidence": 0.50,
            "w_risks": 0.30,
            "w_ethics": 0.20
        }

        adjustments = []

        # Analyze history
        total_runs = len(execution_history)
        successes = sum(1 for r in execution_history if r.get("success", False))
        success_rate = (successes / total_runs) if total_runs > 0 else 1.0

        # Meta-Learning Rule 1: High success rate -> Aggressively reduce difficulty weight to pursue harder, higher-value goals
        if success_rate > 0.85 and total_runs >= 3:
            curiosity_weights["w_d"] = 0.10  # Care less about difficulty, pursue harder skills
            curiosity_weights["w_v"] = 0.50  # Value value even more
            adjustments.append(
                "AGGRESSIVE_DIFFICULTY_DEPRECIATION: W_d scaled to 0.10, W_v scaled to 0.50 to prioritize high-value complex tasks."
            )

        # Meta-Learning Rule 2: High failure rate -> Increase risk and compute cost weights (More defensive learning)
        elif success_rate < 0.60 and total_runs >= 3:
            curiosity_weights["w_r"] = 0.35  # Care more about risks
            curiosity_weights["w_c"] = 0.20  # Care more about compute cost
            wisdom_weights["w_risks"] = 0.40  # Tighten safety limits
            adjustments.append(
                "DEFENSIVE_RISK_MITIGATION: Scaled up W_r and W_risks to tighten safety filters on candidate skill trials."
            )

        # Persist optimized meta-coefficients as an SOK rule card in SQLite
        card_id = "SOK-META-LEARNING-ALGORITHMS-COEFFICIENTS"
        content = (
            f"AUTONOMOUS META-LEARNING ALGORITHM OPTIMIZATION.\n"
            f"Calibrated Weights:\n"
            f"  - Curiosity Weights: {curiosity_weights}\n"
            f"  - Wisdom Weights: {wisdom_weights}\n"
            f"Adjustments Applied: {adjustments if adjustments else 'No adjustments needed yet.'}"
        )
        focus = "Meta-learning loop coefficients tune"
        self.db.upsert_card(
            card_id=card_id,
            family="Knowledge",
            focus=focus,
            content=content,
            status="ACTIVE"
        )
        self.db.update_card_status(card_id, "ACTIVE")

        return {
            "status": "success",
            "meta_learning_rounds": 1,
            "success_rate_analyzed": round(success_rate, 2),
            "adjustments_applied": adjustments,
            "optimized_curiosity_weights": curiosity_weights,
            "optimized_wisdom_weights": wisdom_weights,
            "db_persisted_id": card_id,
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "Restart the perpetual loop. The curiosity and experiment engines will now "
                "autonomously utilize these tuned coefficients to optimize future discoveries!</span>"
            )
        }
