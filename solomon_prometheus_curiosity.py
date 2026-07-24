"""
Prometheus Curiosity Engine & Self-Directed Knowledge Discovery Loop (SOSS Phase 10)

This module implements the Curiosity Engine that proactively scans SOK cards
for confidence deficits, failure signals, and structural relational gaps, and compiles
prioritized Learning Opportunities (LOs) using a multi-variable weighting matrix.
"""

from typing import List, Dict, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB

class PrometheusCuriosityEngine:
    """
    Core engine responsible for scanning cognitive memory, identifying knowledge gaps,
    and generating prioritized curiosity discovery cards.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def discover_gaps(self) -> List[Dict[str, Any]]:
        """
        Scans all cognitive cards in the database, maps their confidence ratings,
        evaluates structural incoming/outgoing links, and scores their gap opportunity index.

        Opportunity Weight = (2.0 - Confidence) * (1.0 + SimulatedFailureRate) + 1 / (1 + LinkCount)
        """
        all_cards = self.db.get_all_cards()
        gaps = []

        for card_summary in all_cards:
            card_id = card_summary["card_id"]
            card_detail = self.db.get_card(card_id)
            if not card_detail:
                continue

            confidence = card_detail.get("confidence", 1.0)
            outgoing_count = len(card_detail.get("outgoing_links", []))
            incoming_count = len(card_detail.get("incoming_links", []))
            total_links = outgoing_count + incoming_count

            # Simulate a failure rate based on how low the confidence rating is
            # lower confidence implies higher operational vulnerability
            simulated_failure_rate = max(0.0, 1.0 - confidence)

            # Multi-variable Opportunity Weighting Matrix computation
            opportunity_weight = (2.0 - confidence) * (1.0 + simulated_failure_rate) + (1.0 / (1.0 + total_links))
            opportunity_weight = round(opportunity_weight, 4)

            # Flag a gap if confidence is below 0.95 or if it is completely isolated
            is_gap = (confidence < 0.95) or (total_links == 0)

            if is_gap:
                # Compile gap details
                gaps.append({
                    "card_id": card_id,
                    "family": card_detail["family"],
                    "focus": card_detail["focus"],
                    "content": card_detail["content"],
                    "confidence": confidence,
                    "total_links": total_links,
                    "simulated_failure_rate": round(simulated_failure_rate, 4),
                    "opportunity_weight": opportunity_weight,
                    "proposed_hypothesis": f"Optimizing the execution parameters and structural connections of {card_id} will mitigate an estimated {round(simulated_failure_rate * 100, 2)}% risk factor."
                })

        # Sort gaps descending by opportunity weight (highest opportunity first)
        gaps.sort(key=lambda x: x["opportunity_weight"], reverse=True)
        return gaps

    def register_curiosity_card(self, gap: Dict[str, Any]) -> str:
        """
        Synthesizes a new Curiosity-type card in the Mnemosyne database to formally
        document the identified knowledge gap as an actionable target.
        """
        curiosity_id = f"SOK-CURIOSITY-{gap['card_id'].replace('SOK-', '')}"
        family = "Task"
        focus = f"Curiosity Discovery: Close gap in {gap['card_id']}"
        content = (
            f"Resolve the cognitive vulnerability identified in {gap['card_id']}. "
            f"The card has a confidence of {gap['confidence']} and a relational density score of {gap['total_links']}. "
            f"Hypothesis: {gap['proposed_hypothesis']}"
        )

        # Save to SQLite database
        self.db.upsert_card(curiosity_id, family, focus, content)

        # Connect the curiosity card to the source card
        self.db.add_link(curiosity_id, gap["card_id"], "REMEDIES")

        return curiosity_id
