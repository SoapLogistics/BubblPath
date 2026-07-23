"""
Solomon Perpetual Learning Machine
Phase 16: Collaborative RAG Knowledge Synchronization

This module implements secure, collaborative knowledge synchronization across
different nodes, allowing secure RAG vector embeddings, metadata, and relational
links transfer between local servers, cloud, and edge.
"""

import json
from typing import Dict, Any, List
from solomon_mnemosyne_db import SolomonMnemosyneDB

class CollaborativeRAGSync:
    """
    Manages secure, collaborative sharing and merging of SOK RAG knowledge
    and directed link structures between active nodes.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def export_local_sok_catalog(self) -> str:
        """
        Exports all local SOK knowledge cards and relational links into a secure JSON string.
        """
        cards = self.db.get_all_cards()
        sync_payload = []

        for card in cards:
            cid = card["card_id"]
            detailed = self.db.get_card(cid)
            sync_payload.append({
                "card_id": cid,
                "family": detailed.get("family"),
                "focus": detailed.get("focus"),
                "content": detailed.get("content"),
                "confidence": detailed.get("confidence", 1.0),
                "validation_state": detailed.get("validation_state", "ACTIVE"),
                "outgoing_links": detailed.get("outgoing_links", [])
            })

        return json.dumps(sync_payload, indent=2)

    def import_and_merge_peer_catalog(self, catalog_json: str) -> Dict[str, Any]:
        """
        Imports and collaboratively merges a peer node's SOK cards and relational links.
        Resolves conflicts by preserving the card with the highest confidence level.
        """
        try:
            peer_cards = json.loads(catalog_json)
        except json.JSONDecodeError as je:
            return {"success": False, "error": f"Invalid catalog JSON format: {str(je)}"}

        merged_cards = 0
        added_links = 0

        for r_card in peer_cards:
            card_id = r_card.get("card_id")
            if not card_id:
                continue

            local_card = self.db.get_card(card_id)
            should_merge = False

            if not local_card:
                should_merge = True
            else:
                # Merge if remote confidence is higher
                if float(r_card.get("confidence", 1.0)) > float(local_card.get("confidence", 1.0)):
                    should_merge = True

            if should_merge:
                # Upsert SOK card
                self.db.upsert_card(
                    card_id=card_id,
                    family=r_card.get("family", "Knowledge"),
                    focus=r_card.get("focus", "Synced focus"),
                    content=r_card.get("content", ""),
                    validation_state=r_card.get("validation_state", "ACTIVE")
                )

                # Apply confidence scaling
                r_conf = float(r_card.get("confidence", 1.0))
                l_conf = float(local_card.get("confidence", 1.0)) if local_card else 1.0
                if r_conf != l_conf:
                    self.db.update_card_confidence(card_id, "success", learning_rate=(r_conf / l_conf) - 1.0)

                # Merge relational links
                for link in r_card.get("outgoing_links", []):
                    target_id = link.get("target_id")
                    rel_type = link.get("relationship_type")
                    if target_id and rel_type:
                        self.db.add_link(card_id, target_id, rel_type)
                        added_links += 1

                merged_cards += 1

        return {
            "success": True,
            "cards_merged": merged_cards,
            "relational_links_added": added_links
        }
