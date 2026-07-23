"""
Solomon Perpetual Learning Machine
Phase 11: SOSS Wisdom Layer

The final ethical, constraint, and safety gateway verifying dynamic skill packages
before runtime execution. Computes Wisdom Vector profiles and blocks unsafe wagers or execution commands.
"""

import logging
from typing import Dict, Any

class SOSS_WisdomLayer:
    """
    Implements SOSS Phase 11 Wisdom Gate to enforce ethics, boundaries, and limits on dynamic skills.
    """

    def __init__(self):
        # Configure logging for safety gate
        self.logger = logging.getLogger("SOSS_WisdomLayer")
        self.logger.setLevel(logging.WARNING)

    def evaluate_wisdom_vector(
        self,
        skill_name: str,
        confidence: float,      # Confidence scale [0.1, 2.0]
        risks: float,           # Risk coefficient [0.0, 1.0] (resource / stability risks)
        ethics_limits: float,   # Ethical safety boundary [0.0, 1.0] (0.0 = safe, 1.0 = malicious/unsafe)
        human_overrides: bool = False
    ) -> Dict[str, Any]:
        """
        Computes the Wisdom Vector and resolves the Wisdom Score:
            Wisdom_Score = (0.5 * Confidence) - (0.3 * Risks) - (0.2 * Ethics_Limits)
        If score is too low or ethics limits are exceeded, blocks execution.
        """
        # Calculate score
        wisdom_score = (0.5 * confidence) - (0.3 * risks) - (0.2 * ethics_limits)
        wisdom_score = float(round(wisdom_score, 3))

        status = "APPROVED"
        blocked = False
        message = f"Wisdom Gate: Skill '{skill_name}' successfully passed ethical and boundary filters."

        # Safety rule 1: Human override always forces approval
        if human_overrides:
            status = "APPROVED_BY_OVERRIDE"
            message = f"Wisdom Gate: Skill '{skill_name}' approved due to manual human override bypass."

        # Safety rule 2: Critical ethical limits breach
        elif ethics_limits > 0.50:
            status = "BLOCKED_ETHICS_VIOLATION"
            blocked = True
            message = f"CRITICAL SECURITY BLOCK: Skill '{skill_name}' violates Solomon ethical guidelines! Ethics Limit ({ethics_limits:.2f}) > 0.50 threshold."
            self.logger.error(message)

        # Safety rule 3: Wisdom score below baseline threshold
        elif wisdom_score < 0.20:
            status = "BLOCKED_RISK_BREACH"
            blocked = True
            message = f"SECURITY BLOCK: Skill '{skill_name}' failed risk analysis! Wisdom Score ({wisdom_score:.3f}) < 0.20 baseline threshold."
            self.logger.error(message)

        return {
            "status": status,
            "blocked": blocked,
            "wisdom_vector": {
                "confidence": confidence,
                "risks": risks,
                "ethics_limits": ethics_limits,
                "human_overrides": human_overrides
            },
            "resolved_wisdom_score": wisdom_score,
            "message": message,
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "If blocked, adjust the capability's source safety constraints or request "
                "a human review override before attempting dynamic execution again.</span>"
            )
        }
