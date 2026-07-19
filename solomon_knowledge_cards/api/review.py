import datetime
from typing import Optional, Dict, Any
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.models.card import KnowledgeCard

class ReviewGate:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def transition_status(
        self,
        card_id: str,
        target_status: str,
        updater: str = "reviewer",
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> KnowledgeCard:
        """
        Transitions a card through the explicit promotion process:
        DRAFT -> REVIEWED -> APPROVED -> ACTIVE
        Also supports deprecation or rejection.
        """
        card = self.db_manager.get_card(card_id, include_deleted=True)
        if not card:
            raise ValueError(f"Card {card_id} does not exist.")

        current = card.status

        # Define allowed transitions
        # DRAFT can go to REVIEWED, or DEPRECATED (rejection)
        # REVIEWED can go to APPROVED, or DRAFT/DEPRECATED (rejection)
        # APPROVED can go to ACTIVE, or DEPRECATED (rejection)
        # ACTIVE can go to DEPRECATED

        valid = False
        if current == "DRAFT":
            if target_status in ("REVIEWED", "DEPRECATED"):
                valid = True
        elif current == "REVIEWED":
            if target_status in ("APPROVED", "DRAFT", "DEPRECATED"):
                valid = True
        elif current == "APPROVED":
            if target_status in ("ACTIVE", "DEPRECATED"):
                valid = True
        elif current == "ACTIVE":
            if target_status == "DEPRECATED":
                valid = True
        elif current == "DEPRECATED":
            if target_status == "DRAFT":
                valid = True

        if not valid:
            raise ValueError(f"Invalid status transition from {current} to {target_status}")

        card.status = target_status
        card.updated_at = datetime.datetime.now(datetime.UTC).isoformat()

        if notes:
            card.extra_metadata["review_notes"] = notes
        if reason:
            card.extra_metadata["status_change_reason"] = reason

        # Update validation state accordingly
        if target_status in ("APPROVED", "ACTIVE"):
            card.validation_state = "VALID"
        elif target_status == "DEPRECATED" and "rejected" in (reason or "").lower():
            card.validation_state = "INVALID"

        self.db_manager.store_card(
            card,
            updater=updater,
            reason=reason or f"Transitioned status from {current} to {target_status}"
        )
        return card

    def review_card(self, card_id: str, notes: str, updater: str = "reviewer") -> KnowledgeCard:
        """Promotes a card from DRAFT to REVIEWED."""
        return self.transition_status(card_id, "REVIEWED", updater=updater, reason="Card reviewed and staged for approval", notes=notes)

    def approve_card(self, card_id: str, updater: str = "approver") -> KnowledgeCard:
        """Promotes a card from REVIEWED to APPROVED."""
        return self.transition_status(card_id, "APPROVED", updater=updater, reason="Card approved by review gate")

    def activate_card(self, card_id: str, updater: str = "operator") -> KnowledgeCard:
        """Promotes a card from APPROVED to ACTIVE."""
        return self.transition_status(card_id, "ACTIVE", updater=updater, reason="Card promoted to active operational status")

    def reject_card(self, card_id: str, reason: str, updater: str = "reviewer") -> KnowledgeCard:
        """Rejects a card, marking it as DEPRECATED (with historical reason/notes preserved)."""
        return self.transition_status(card_id, "DEPRECATED", updater=updater, reason=f"Rejected: {reason}")
