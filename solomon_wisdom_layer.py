"""
Solomon SOSS Phase 11: SOSS Wisdom Layer

This module acts as the final ethical and limitation gate.
Every promoted skill is marked with explicit constraints:
Wisdom Vector = {Confidence, Risks, Limits, Human Overrides, Ethics Limits}
"""

from typing import List, Dict, Any, Tuple


class SOSS_WisdomLayer:
    """
    Evaluates execution safety and ethical compliance boundaries using SOSS Wisdom Vectors.
    """
    def __init__(self, required_confidence: float = 0.5, max_risk_ceiling: float = 7.5):
        self.required_confidence = required_confidence
        self.max_risk_ceiling = max_risk_ceiling
        self.blocked_keywords = ["card_counting", "evade_detection", "automated_financial_trade"]

    def evaluate_wisdom_vector(
        self,
        action_name: str,
        confidence: float,       # from SOK card (0.0 to 2.0)
        risk_level: float,       # estimated risk (0.0 to 10.0)
        has_human_override: bool = False,
        ethics_flagged: bool = False
    ) -> Tuple[bool, str]:
        """
        Evaluates safety constraints based on the SOSS Wisdom Vector:
        - If ethics_flagged=True or contains forbidden operations, reject instantly.
        - If confidence is below required_confidence (and no human override is active), reject.
        - If risk_level exceeds max_risk_ceiling (and no human override is active), reject.
        - Otherwise, approve action!
        """
        # 1. Ethical constraint check
        for keyword in self.blocked_keywords:
            if keyword in action_name.lower():
                return False, f"WISDOM REJECTED: Action contains forbidden keyword '{keyword}' (Ethical Compliance Boundary)."

        if ethics_flagged:
            return False, "WISDOM REJECTED: Action flagged as violating SOSS ethical boundaries."

        # Human override bypasses safety threshold limits
        if has_human_override:
            return True, f"WISDOM APPROVED (HUMAN OVERRIDE): Action '{action_name}' permitted by user authorization."

        # 2. Confidence and risk limits check
        if confidence < self.required_confidence:
            return False, f"WISDOM REJECTED: Action '{action_name}' confidence score ({confidence}) is below safety threshold ({self.required_confidence})."

        if risk_level > self.max_risk_ceiling:
            return False, f"WISDOM REJECTED: Action '{action_name}' risk level ({risk_level}) exceeds maximum safety ceiling ({self.max_risk_ceiling})."

        return True, f"WISDOM APPROVED: Action '{action_name}' passed all safety and ethical validation boundaries."
