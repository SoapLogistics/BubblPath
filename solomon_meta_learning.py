"""
Solomon Perpetual Learning Machine
Phase 12: Learning How to Learn (Meta-Learning)

This module implements Solomon's final evolutionary step.
Instead of just acquiring Python scripts or tuning simple parameters,
it optimizes the structural algorithms of the Experiment Engine and the Review Gate itself.
"""

from typing import Dict, Any, List

class MetaLearningEngine:
    """
    Autonomously refactors structural algorithms and tunes meta-parameters
    of the Curiosity and Experiment Engines to transition learning growth
    from additive to exponential.
    """

    @classmethod
    def execute_meta_learning_tuning(
        cls,
        current_learning_speed_ratio: float, # e.g. 1.05 (representing 5% hour-over-hour speedup)
        historical_speeds: List[float],
        curiosity_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Tunes the core coefficients of the Curiosity weighting formula dynamically.
        """
        trace = []
        trace.append("Meta-Learning: Initializing structural self-refactoring pass...")

        # Calculate momentum (rate of change of our learning speed)
        if len(historical_speeds) >= 2:
            momentum = current_learning_speed_ratio - historical_speeds[-1]
        else:
            momentum = 0.01

        trace.append(f"Meta-Learning: Detected system momentum: {momentum:+.4f}")

        tuned_weights = curiosity_weights.copy()
        structural_refactorings = []

        # If learning speed is decelerating or stagnating (momentum <= 0),
        # autonomously refactor curiosity weights to favor high value and lower risk
        if momentum <= 0:
            trace.append("Meta-Learning: Stagnation detected! Executing structural curiosity refactoring...")

            # Boost the value weight coefficient
            old_val = tuned_weights.get("w_value", 1.5)
            tuned_weights["w_value"] = round(old_val + 0.2, 2)
            structural_refactorings.append(
                f"Boosted curiosity 'w_value' from {old_val} to {tuned_weights['w_value']} to focus on high-impact targets."
            )

            # Reduce risk tolerance coefficient
            old_risk = tuned_weights.get("w_risk", 0.8)
            tuned_weights["w_risk"] = round(old_risk + 0.1, 2) # Higher w_risk means risk is penalized more heavily
            structural_refactorings.append(
                f"Increased risk penalty 'w_risk' from {old_risk} to {tuned_weights['w_risk']} to avoid system degradation."
            )
        else:
            trace.append("Meta-Learning: Growth momentum is positive. Maintaining active structural configuration.")

        return {
            "meta_learning_momentum": round(momentum, 4),
            "original_curiosity_weights": curiosity_weights,
            "tuned_curiosity_weights": tuned_weights,
            "structural_refactorings_triggered": structural_refactorings,
            "growth_category": "EXPONENTIAL" if momentum > 0 else "STAGNANT_ADAPTING",
            "status": "META_LEARNING_COMPLETE"
        }
