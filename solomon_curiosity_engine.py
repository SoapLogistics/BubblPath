"""
Solomon SOSS Phase 2: Curiosity Engine (Prometheus Opportunity Mapper)

This module identifies knowledge gaps, evaluates Learning Opportunities (LOs),
computes LO scores using the Opportunity Weighting Matrix, and incorporates the
Albert Einstein Absurdity heuristic to incentivize breakthrough concepts.
"""

import math
from typing import List, Dict, Any, Tuple


class LearningOpportunity:
    """
    Represents an identified learning opportunity / knowledge gap in Solomon's database.
    """
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        value: float,       # w_v component (0.0 to 10.0)
        difficulty: float,  # w_d component (0.0 to 10.0)
        future_use: float,  # w_u component (0.0 to 10.0)
        risk: float,        # w_r component (0.0 to 10.0)
        compute_cost: float, # w_c component (0.0 to 10.0)
        is_absurd: bool = False, # Einstein heuristic flag
        metadata: Dict[str, Any] = None
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.value = value
        self.difficulty = difficulty
        self.future_use = future_use
        self.risk = risk
        self.compute_cost = compute_cost
        self.is_absurd = is_absurd
        self.metadata = metadata or {}
        self.lo_score = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "value": self.value,
            "difficulty": self.difficulty,
            "future_use": self.future_use,
            "risk": self.risk,
            "compute_cost": self.compute_cost,
            "is_absurd": self.is_absurd,
            "lo_score": round(self.lo_score, 2),
            "metadata": self.metadata
        }


class CuriosityEngine:
    """
    Prometheus Opportunity Mapper that manages the queue of learning opportunities.
    Computes scores and balances risk using the Albert Einstein absurdity principle:
    "If at first the idea is not absurd, then there is no hope for it."
    """
    def __init__(
        self,
        w_v: float = 1.5, # Value weight
        w_d: float = 1.0, # Difficulty weight (can incentivize harder tasks for greater learning)
        w_u: float = 2.0, # Future utility weight
        w_r: float = 1.2, # Risk weight
        w_c: float = 0.8  # Compute cost weight
    ):
        self.w_v = w_v
        self.w_d = w_d
        self.w_u = w_u
        self.w_r = w_r
        self.w_c = w_c
        self.learning_queue: List[LearningOpportunity] = []

    def calculate_lo_score(self, lo: LearningOpportunity) -> float:
        """
        Calculates the Learning Opportunity Score using the Opportunity Weighting Matrix:
        LO_Score = w_v * Value + w_d * Difficulty + w_u * FutureUse - w_r * Risk - w_c * ComputeCost

        If the idea is flagged as 'is_absurd', we apply Albert Einstein's absurdity multiplier,
        which boosts the FutureUse potential and neutralizes the high risk penalty.
        """
        # Base components
        val_term = self.w_v * lo.value
        diff_term = self.w_d * lo.difficulty
        util_term = self.w_u * lo.future_use
        risk_term = self.w_r * lo.risk
        comp_term = self.w_c * lo.compute_cost

        # Under normal conditions, risk is subtracted.
        # But if the idea is absurd, Einstein's heuristic tells us there is hope!
        # We boost the utility term and reduce the penalty of risk by half.
        if lo.is_absurd:
            # Einstein Absurdity Bonus
            util_term *= 1.8  # Unlocks massive future potential
            risk_term *= 0.4  # Neutralizes the risk fear barrier
            absurdity_bonus = 5.0
        else:
            absurdity_bonus = 0.0

        score = val_term + diff_term + util_term - risk_term - comp_term + absurdity_bonus
        lo.lo_score = max(score, -100.0) # Lower bound sanity check
        return lo.lo_score

    def scan_feedback_for_gaps(self, system_logs: List[Dict[str, Any]]) -> List[LearningOpportunity]:
        """
        Scans trace logs or database execution feedback to automatically
        discover new knowledge gaps / learning opportunities.
        """
        discovered_gaps = []
        for log in system_logs:
            event_type = log.get("event_type", "")
            outcome = log.get("outcome", "")
            error_msg = log.get("error_msg", "")
            feature_name = log.get("feature_name", "Unknown Feature")

            if outcome == "failure" or event_type == "RECURSIVE_CRUCIBLE_FAIL":
                # Create a high-priority Learning Opportunity to solve this failure
                lo = LearningOpportunity(
                    task_id=f"LO-GAP-{abs(hash(feature_name)) % 10000}",
                    title=f"Repair and Assimilate {feature_name}",
                    description=f"Auto-discovered failure gap: '{error_msg}' inside {feature_name}.",
                    value=8.5,       # High value to repair system crashes
                    difficulty=6.0,  # Medium difficulty
                    future_use=9.0,  # High future utility to prevent future failures
                    risk=3.0,        # Lower risk to patch
                    compute_cost=2.0,
                    is_absurd=False,
                    metadata={"source_log": log}
                )
                discovered_gaps.append(lo)
        return discovered_gaps

    def register_opportunity(self, lo: LearningOpportunity):
        """
        Adds a new Learning Opportunity to the Prometheus tracking queue.
        """
        # Calculate the score immediately upon registration
        self.calculate_lo_score(lo)
        self.learning_queue.append(lo)

    def get_priority_queue(self) -> List[LearningOpportunity]:
        """
        Returns all registered Learning Opportunities sorted by LO Score in descending order.
        """
        # Recalculate scores to reflect any weight tuning changes
        for lo in self.learning_queue:
            self.calculate_lo_score(lo)

        # Sort descending
        return sorted(self.learning_queue, key=lambda x: x.lo_score, reverse=True)

    def select_next_best_learning_task(self) -> Tuple[LearningOpportunity, str]:
        """
        Selects the top-priority learning task, returning it along with a philosophical
        recommendation based on Albert Einstein.
        """
        queue = self.get_priority_queue()
        if not queue:
            # Fallback to an elegant template
            fallback_lo = LearningOpportunity(
                task_id="LO-EINSTEIN-ABSURDITY",
                title="Explore Quantum Weight Rotations",
                description="Simulate extreme ternary weight state transformations.",
                value=9.0,
                difficulty=8.5,
                future_use=9.5,
                risk=8.0,
                compute_cost=5.0,
                is_absurd=True
            )
            self.register_opportunity(fallback_lo)
            queue = [fallback_lo]

        selected = queue[0]
        quote = "“If at first the idea is not absurd, then there is no hope for it.” — Albert Einstein"
        recommendation = f"Prometheus recommendation: Focus on '{selected.title}'. {quote if selected.is_absurd else ''}"
        return selected, recommendation
