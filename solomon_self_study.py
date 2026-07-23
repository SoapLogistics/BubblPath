"""
Solomon Perpetual Learning Machine
Phase 6: Learning Process Optimization (Self-Study)

This module implements dynamic self-tuning. It analyzes system-wide metrics
(such as semantic retrieval success rates and sandbox execution accuracy)
to programmatically optimize vector weights, thresholds, and decay rates.
"""

from typing import Dict, Any

class SelfStudyOptimizer:
    """
    Autonomously tunes active RAG and Model Router hyperparameters based on
    rolling execution feedback, maximizing retrieval relevance and routing accuracy.
    """

    @classmethod
    def optimize_hyperparameters(
        cls,
        retrieval_success_rate: float, # rolling rate, e.g. 0.88
        router_accuracy_rate: float,    # e.g. 0.92
        current_params: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Dynamically adjusts active hyperparameters based on performance metrics.
        """
        tuned_params = current_params.copy()
        adjustments_made = []

        # 1. Low retrieval success -> Increase base threshold to increase target model safety,
        # or tune decay factor to preserve memory relevance
        if retrieval_success_rate < 0.90:
            old_threshold = tuned_params.get("base_threshold", 0.40)
            tuned_params["base_threshold"] = min(0.80, old_threshold + 0.05)
            adjustments_made.append(
                f"Retrieved card relevance is low ({retrieval_success_rate:.2f}). "
                f"Tuned 'base_threshold' from {old_threshold:.2f} to {tuned_params['base_threshold']:.2f} for higher safety."
            )

        # 2. Low router accuracy -> Adjust vector weights to favor high-confidence links
        if router_accuracy_rate < 0.95:
            old_decay = tuned_params.get("similarity_decay", 0.98)
            tuned_params["similarity_decay"] = max(0.90, old_decay - 0.02)
            adjustments_made.append(
                f"Router selection accuracy is sub-optimal ({router_accuracy_rate:.2f}). "
                f"Optimized 'similarity_decay' from {old_decay:.2f} to {tuned_params['similarity_decay']:.2f} to discard obsolete entries."
            )

        if not adjustments_made:
            adjustments_made.append("All retrieval and routing parameters are perfectly balanced. Hyperparameters maintained.")

        return {
            "performance_inputs": {
                "retrieval_success_rate": retrieval_success_rate,
                "router_accuracy_rate": router_accuracy_rate
            },
            "optimized_hyperparameters": tuned_params,
            "adjustments_made": adjustments_made,
            "status": "PARAMETERS_OPTIMIZED"
        }
