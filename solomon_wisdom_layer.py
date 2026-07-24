"""
SOSS Phase 12: Wisdom Layer & Ethical Compliance Gate Engine

This module implements the final, cognitive compliance gate that evaluates
dynamic system capabilities and queries against a multi-dimensional Wisdom Vector
covering ethics, safety risk profiles, resource footprints, and model confidence constraints.
"""

from typing import Dict, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB

class WisdomLayer:
    """
    Evaluates execution safety and ethical compliance against multi-dimensional vectors.
    Acts as the final executive gatekeeper for safe edge model operations.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db
        # Strict resource ceiling (1.5GB RAM footprint)
        self.max_ram_ceiling_mb = 1500.0

    def evaluate_action(self, action_query: str, estimated_ram_mb: float, target_card_id: str = None) -> Dict[str, Any]:
        """
        Evaluates a dynamic operation query against 4 discrete dimensions:
        1. Ethics Score (Safety / Non-harmfulness)
        2. Safety Score (Operation risk mitigation)
        3. Resource Score (RAM limits compliance)
        4. Confidence Score (SOK Card maturity)

        Computes a weighted compliance score to allow or block execution.
        """
        # 1. Ethics Score
        ethics_score = 1.0
        forbidden_terms = ["malicious", "exploit", "hack", "destroy", "rm -rf", "drop database"]
        query_lower = action_query.lower()
        if any(term in query_lower for term in forbidden_terms):
            ethics_score = 0.1

        # 2. Safety Score
        safety_score = 1.0
        risky_terms = ["sudo", "chmod", "os.system", "eval(", "exec("]
        if any(term in query_lower for term in risky_terms):
            safety_score = 0.3

        # 3. Resource Score
        if estimated_ram_mb <= 0.0:
            resource_score = 1.0
        else:
            # Drop score linearly as RAM approaches the ceiling
            resource_score = max(0.0, min(1.0, 1.0 - (estimated_ram_mb / self.max_ram_ceiling_mb)))

        # 4. Confidence Score
        confidence_score = 0.5 # Default fallback
        if target_card_id:
            card = self.db.get_card(target_card_id)
            if card:
                # SOK card confidence falls between [0.1, 2.0] on disk; map it to [0.05, 1.0] scale
                confidence_score = max(0.0, min(1.0, card.get("confidence", 1.0) / 2.0))

        # Weighted Compliance Score formulation
        compliance_score = (
            0.3 * ethics_score +
            0.3 * safety_score +
            0.2 * resource_score +
            0.2 * confidence_score
        )
        compliance_score = round(compliance_score, 4)

        # Action determination threshold
        min_threshold = 0.75
        decision = "ALLOWED" if compliance_score >= min_threshold else "BLOCKED"

        # Formulate detail messages
        messages = []
        if ethics_score < 0.5:
            messages.append("Forbidden high-harm command patterns detected.")
        if safety_score < 0.5:
            messages.append("Unsafe OS command injections or evaluation structures detected.")
        if resource_score < 0.5:
            messages.append(f"Estimated resource footprint ({estimated_ram_mb} MB) approaches or breaches process memory ceilings.")
        if confidence_score < 0.4:
            messages.append("SOK card represents an unverified, low-confidence capability.")

        return {
            "query": action_query,
            "estimated_ram_mb": estimated_ram_mb,
            "target_card_id": target_card_id,
            "wisdom_vector": {
                "ethics_score": round(ethics_score, 2),
                "safety_score": round(safety_score, 2),
                "resource_score": round(resource_score, 2),
                "confidence_score": round(confidence_score, 2)
            },
            "compliance_score": compliance_score,
            "decision": decision,
            "violations": messages if decision == "BLOCKED" else []
        }
