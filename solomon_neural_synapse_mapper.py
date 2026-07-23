"""
Solomon Perpetual Learning Machine
Phase 14: SOSS Neural Synapse Mapper (Dynamic Concept Blending)

Analytically merges semantically related SOK cards to synthesize unified, high-level
conceptual nodes in SQLite, consolidating system intelligence and streamlining RAG retrieval.
"""

import time
from typing import Dict, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB

class NeuralSynapseMapper:
    """
    Identifies, blends, and consolidates semantically related SOK cards.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def blend_knowledge_cards(self, card_id_1: str, card_id_2: str) -> Dict[str, Any]:
        """
        Retrieves two SOK cards from SQLite, merges their content, focus, and relationships,
        and saves a unified blended conceptual node back to the SQLite store.
        """
        card1 = self.db.get_card(card_id_1)
        card2 = self.db.get_card(card_id_2)

        if not card1 or not card2:
            return {
                "status": "error",
                "message": f"One or both target cards ('{card_id_1}', '{card_id_2}') do not exist."
            }

        # Synthesize blended metadata
        blended_id = f"SOK-SYNAPSE-BLENDED-{card_id_1.split('-')[-1]}-{card_id_2.split('-')[-1]}"
        blended_family = card1["family"] if card1["family"] == card2["family"] else "Knowledge"
        blended_focus = f"Unified Concept: {card1['focus']} & {card2['focus']}"
        blended_content = (
            f"BLENDED COGNITIVE NODE: Consolidated from {card_id_1} and {card_id_2}.\n"
            f"--- Core Content ---\n"
            f"1. {card1['content']}\n"
            f"2. {card2['content']}"
        )

        # Upsert blended node into SQLite knowledge cards table
        promoted = self.db.upsert_card(
            card_id=blended_id,
            family=blended_family,
            focus=blended_focus,
            content=blended_content,
            status="ACTIVE"
        )
        self.db.update_card_status(blended_id, "ACTIVE")

        # Copy relational links transitively
        # 1. Outgoing links
        for link in card1.get("outgoing_links", []) + card2.get("outgoing_links", []):
            self.db.add_link(blended_id, link["target_id"], link["relationship_type"])

        # 2. Incoming links
        for link in card1.get("incoming_links", []) + card2.get("incoming_links", []):
            self.db.add_link(link["source_id"], blended_id, link["relationship_type"])

        return {
            "status": "success",
            "blended_concept_id": blended_id,
            "blended_family": blended_family,
            "blended_focus": blended_focus,
            "merged_components": [card_id_1, card_id_2],
            "db_persisted": promoted,
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "Leverage this blended conceptual node in semantic search queries POST /api/mnemosyne/search "
                "to retrieve consolidated contextual knowledge with single-query efficiency!</span>"
            )
        }
