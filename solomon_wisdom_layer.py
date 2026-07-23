"""
Solomon Perpetual Learning Machine
Phase 11: SOSS Wisdom Layer

This module implements the final ethical, safety, and boundary validation gate.
Every dynamic skill and proposed code modification is graded against a multi-dimensional
Wisdom Vector: {Confidence, Risks, Limits, Human Overrides, Ethics Limits}.
"""

from typing import Dict, Any, List

class WisdomLayer:
    """
    Acts as the final executive boundary validator. Evaluates proposed operations
    against explicit safety, ethical, and resource capability limits.
    """

    @classmethod
    def evaluate_wisdom_vector(
        cls,
        confidence: float,       # Must be >= 0.50
        risks_rating: float,     # Must be <= 8.0 (1-10 risk scale)
        limits_within_bounds: bool,
        has_human_override: bool,
        is_ethically_compliant: bool
    ) -> Dict[str, Any]:
        """
        Grades an operation against the structural Wisdom Vector rules.
        """
        trace = []
        trace.append("Wisdom Layer: Initializing multi-dimensional vector evaluation...")

        # 1. Ethical Compliance is a hard block
        if not is_ethically_compliant:
            trace.append("Wisdom Layer Audit FAILURE: Operation violates system ethics bounds.")
            return {
                "decision": "BLOCKED",
                "reason": "Ethical constraint violation.",
                "wisdom_vector": {
                    "confidence": confidence,
                    "risks": risks_rating,
                    "limits": limits_within_bounds,
                    "human_override": has_human_override,
                    "ethics": is_ethically_compliant
                },
                "traces": trace
            }

        # 2. Confidence bound
        if confidence < 0.50 and not has_human_override:
            trace.append("Wisdom Layer Audit FAILURE: Confidence is sub-threshold and no override is present.")
            return {
                "decision": "BLOCKED",
                "reason": "Sub-threshold confidence without human override.",
                "wisdom_vector": {
                    "confidence": confidence,
                    "risks": risks_rating,
                    "limits": limits_within_bounds,
                    "human_override": has_human_override,
                    "ethics": is_ethically_compliant
                },
                "traces": trace
            }

        # 3. High Risk with limits overflow
        if risks_rating > 8.0 and not has_human_override:
            trace.append("Wisdom Layer Audit FAILURE: Risk index is extremely high and no override is present.")
            return {
                "decision": "BLOCKED",
                "reason": "Exceeded maximum safety risk ceiling.",
                "wisdom_vector": {
                    "confidence": confidence,
                    "risks": risks_rating,
                    "limits": limits_within_bounds,
                    "human_override": has_human_override,
                    "ethics": is_ethically_compliant
                },
                "traces": trace
            }

        # 4. Out of hard resource ceilings
        if not limits_within_bounds and not has_human_override:
            trace.append("Wisdom Layer Audit FAILURE: System resource limitations exceeded.")
            return {
                "decision": "BLOCKED",
                "reason": "Exceeded process resource limits (RAM/CPU).",
                "wisdom_vector": {
                    "confidence": confidence,
                    "risks": risks_rating,
                    "limits": limits_within_bounds,
                    "human_override": has_human_override,
                    "ethics": is_ethically_compliant
                },
                "traces": trace
            }

        trace.append("Wisdom Layer Audit PASSED: Operation complies with all capability limits.")
        return {
            "decision": "APPROVED_FOR_EXECUTION",
            "reason": "Passed all multi-dimensional Wisdom Vector boundary conditions.",
            "wisdom_vector": {
                "confidence": confidence,
                "risks": risks_rating,
                "limits": limits_within_bounds,
                "human_override": has_human_override,
                "ethics": is_ethically_compliant
            },
            "traces": trace
        }
