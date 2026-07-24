"""
Solomon SOSS Phase 12: Learning How to Learn (Meta-Learning)

This module tracks SOSS learning speed and dynamically optimizes the configurations
and hyperparameters of the Curiosity and Experiment Engines themselves to achieve
exponential knowledge accumulation.
"""

from typing import List, Dict, Any, Tuple
from solomon_curiosity_engine import CuriosityEngine
from solomon_experiment_engine import ExperimentEngine


class MetaLearningEngine:
    """
    Optimizes SOSS learning processes by tracking historical cognitive momentum
    and tuning other engines' core hyper-parameters (such as opportunity weights).
    """
    def __init__(self, curiosity_engine: CuriosityEngine, experiment_engine: ExperimentEngine):
        self.curiosity_engine = curiosity_engine
        self.experiment_engine = experiment_engine
        self.reusable_card_history: List[int] = [] # list of new card counts per epoch

    def record_epoch_progress(self, new_reusable_cards: int):
        self.reusable_card_history.append(new_reusable_cards)

    def optimize_learning_how_to_learn(self) -> Dict[str, Any]:
        """
        Analyzes consecutive epoch progress to evaluate learning momentum:
        - If momentum is slowing down (fewer cards gained), we raise curiosity weights
          (w_v, w_u) to discover more high-value concepts.
        - If momentum is accelerating, we stabilize and slightly tighten safety weights.
        """
        if len(self.reusable_card_history) < 2:
            return {
                "optimized": False,
                "message": "Insufficient historical epochs to evaluate learning momentum."
            }

        prev_gain = self.reusable_card_history[-2]
        current_gain = self.reusable_card_history[-1]

        old_w_v = self.curiosity_engine.w_v
        old_w_u = self.curiosity_engine.w_u

        if current_gain <= prev_gain:
            # Learning speed is flat or decaying. Boost curiosity weights aggressively!
            self.curiosity_engine.w_v = min(self.curiosity_engine.w_v + 0.25, 3.0)
            self.curiosity_engine.w_u = min(self.curiosity_engine.w_u + 0.35, 4.0)
            tuning_mode = "INTENSIFY_CURIOSITY"
        else:
            # Learning speed is accelerating exponentially. Fine-tune and slightly stabilize
            self.curiosity_engine.w_v = max(self.curiosity_engine.w_v - 0.05, 1.0)
            self.curiosity_engine.w_u = max(self.curiosity_engine.w_u - 0.05, 1.0)
            tuning_mode = "STABILIZE_STEADY_STATE"

        return {
            "optimized": True,
            "tuning_mode": tuning_mode,
            "reusable_card_momentum": {
                "prev_gain": prev_gain,
                "current_gain": current_gain,
                "momentum_delta": current_gain - prev_gain
            },
            "calibrated_weights": {
                "old_value_weight": round(old_w_v, 3),
                "new_value_weight": round(self.curiosity_engine.w_v, 3),
                "old_future_use_weight": round(old_w_u, 3),
                "new_future_use_weight": round(self.curiosity_engine.w_u, 3)
            }
        }
