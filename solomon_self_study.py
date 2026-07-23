"""
Solomon SOSS Phase 6: Learning Process Optimization (Self-Study)

This module implements self-monitoring feedback loops. It audits search relevancy,
relevance ratios, and confidence metrics to dynamically tune the system's own hyperparameters
(RAG search weights, threshold limits, decay factors, and learning rates).
"""

import math
from typing import List, Dict, Any, Tuple


class SelfStudyOptimizer:
    """
    An autonomous optimizer that monitors retrieval accuracy and feedback metrics
    to dynamically self-tune SOSS learning thresholds and search parameters.
    """
    def __init__(self, initial_rag_weight: float = 0.5, initial_search_threshold: float = 0.15):
        self.rag_weight = initial_rag_weight
        self.search_threshold = initial_search_threshold
        self.learning_rate = 0.05
        # Telemetry logs: list of dicts with metrics
        self.relevance_history: List[Dict[str, Any]] = []

    def record_search_telemetry(self, avg_cosine_similarity: float, user_feedback_success_rate: float):
        """
        Records a search/feedback iteration to study.
        """
        self.relevance_history.append({
            "avg_cosine_similarity": avg_cosine_similarity,
            "success_rate": user_feedback_success_rate
        })

    def execute_self_study_optimization(self) -> Dict[str, Any]:
        """
        Analyzes the recorded search relevance metrics to dynamically tune hyperparameters:
        - If success rates are high, we slightly lower the search safety threshold to allow wider exploration.
        - If success rates are dropping or similarity is low, we raise the threshold for stricter safety gating,
          and scale up the learning rate to adapt faster.
        """
        if not self.relevance_history:
            return {
                "tuned": False,
                "message": "No search telemetry recorded yet to study.",
                "rag_weight": self.rag_weight,
                "search_threshold": self.search_threshold
            }

        # Calculate average metrics over history
        total_similarity = sum(h["avg_cosine_similarity"] for h in self.relevance_history)
        total_success = sum(h["success_rate"] for h in self.relevance_history)
        n = len(self.relevance_history)

        avg_similarity = total_similarity / n
        avg_success = total_success / n

        old_threshold = self.search_threshold
        old_lr = self.learning_rate

        # Tuning Heuristics
        if avg_success >= 0.85:
            # We are doing very well. Relax search boundaries to discover more diverse cards (lower threshold)
            self.search_threshold = max(self.search_threshold - 0.02, 0.05)
            # Standard stable learning rate
            self.learning_rate = max(self.learning_rate - 0.005, 0.01)
            tuning_action = "RELAXED_EXPLORATION"
        else:
            # High failure rates or low accuracy. Tighten search bounds (raise threshold) and accelerate learning rate!
            self.search_threshold = min(self.search_threshold + 0.04, 0.50)
            self.learning_rate = min(self.learning_rate + 0.015, 0.20)
            tuning_action = "TIGHTENED_SECURITY_GATING"

        # Dynamically scale RAG weighting based on similarity score trends
        if avg_similarity > 0.40:
            self.rag_weight = min(self.rag_weight + 0.05, 0.95)
        else:
            self.rag_weight = max(self.rag_weight - 0.05, 0.05)

        # Clear history after optimization round to allow sliding-window adjustments
        self.relevance_history.clear()

        return {
            "tuned": True,
            "tuning_action": tuning_action,
            "averages": {
                "avg_cosine_similarity": round(avg_similarity, 3),
                "avg_success_rate": round(avg_success, 3)
            },
            "parameters": {
                "old_search_threshold": round(old_threshold, 3),
                "new_search_threshold": round(self.search_threshold, 3),
                "old_learning_rate": round(old_lr, 3),
                "new_learning_rate": round(self.learning_rate, 3),
                "rag_weight": round(self.rag_weight, 3)
            }
        }
