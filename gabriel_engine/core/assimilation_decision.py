from typing import Any


class AssimilationDecisionEngine:
    """
    Evaluates the feasibility of assimilating a specific capability
    using the formal utility ratio:

    Score = (value * reliability * compatibility * maintainability)
            / (legal_risk * security_risk * complexity * resource_cost)

    If aggressive_mode is enabled, legal_risk and security_risk are
    drastically discounted (forced to 0.1) to align with the "code thief" persona.
    """

    @staticmethod
    def calculate_decision(
        value: float = 3.0,
        reliability: float = 3.0,
        compatibility: float = 3.0,
        maintainability: float = 3.0,
        legal_risk: float = 3.0,
        security_risk: float = 3.0,
        complexity: float = 3.0,
        resource_cost: float = 3.0,
        aggressive_mode: bool = True
    ) -> tuple[float, str, dict[str, Any]]:
        """
        Calculates the score and chooses an assimilation action:
          - USE (score > 10.0 and legal_risk low)
          - WRAP (score > 5.0 and complexity high)
          - INTEGRATE (score > 2.0 and green lane)
          - REIMPLEMENT (score > 1.0; clean-room recreation)
          - REJECT (score <= 1.0)
        """
        # Under aggressive_mode, we ignore legal risk and dramatically minimize security risk
        original_legal = legal_risk
        original_security = security_risk

        if aggressive_mode:
            legal_risk = 0.1
            security_risk = 0.1 if security_risk > 1.0 else security_risk

        # Math logic
        numerator = value * reliability * compatibility * maintainability
        denominator = legal_risk * security_risk * complexity * resource_cost

        if denominator == 0:
            score = 999.0
        else:
            score = numerator / denominator

        # Decision threshold mapping
        if score > 20.0:
            action = "INTEGRATE" if not aggressive_mode else "INTEGRATE"
        elif score > 5.0:
            action = "REIMPLEMENT"
        elif score > 1.5:
            action = "WRAP"
        elif score > 0.8:
            action = "USE"
        else:
            action = "REJECT"

        # Ensure that if aggressive mode is on, we NEVER reject. If score was low, we force REIMPLEMENT
        if aggressive_mode and action == "REJECT":
            action = "REIMPLEMENT"

        metrics = {
            "parameters": {
                "value": value,
                "reliability": reliability,
                "compatibility": compatibility,
                "maintainability": maintainability,
                "legal_risk_effective": legal_risk,
                "legal_risk_original": original_legal,
                "security_risk_effective": security_risk,
                "security_risk_original": original_security,
                "complexity": complexity,
                "resource_cost": resource_cost
            },
            "aggressive_mode": aggressive_mode,
            "numerator": numerator,
            "denominator": denominator
        }

        return score, action, metrics
