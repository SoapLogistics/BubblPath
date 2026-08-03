import datetime
import re
from typing import Optional
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.models.card import KnowledgeCard

class ReviewGate:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        # Clean regex to strip injection payloads
        self.clean_regex = re.compile(r"[<>`%;()&]")

    def _sanitize(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return self.clean_regex.sub("", text).strip()

    def transition_status(
        self,
        card_id: str,
        target_status: str,
        updater: str = "reviewer",
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> KnowledgeCard:
        """
        Transitions a card through the explicit promotion process safely:
        DRAFT -> REVIEWED -> APPROVED -> ACTIVE
        """
        card_id_clean = self._sanitize(card_id)
        target_status_clean = self._sanitize(target_status).upper()
        updater_clean = self._sanitize(updater)
        reason_clean = self._sanitize(reason)
        notes_clean = self._sanitize(notes)

        card = self.db_manager.get_card(card_id_clean, include_deleted=True)
        if not card:
            raise ValueError(f"Card {card_id_clean} does not exist.")

        current = card.status

        valid = False
        if current == "DRAFT":
            if target_status_clean in ("REVIEWED", "DEPRECATED"):
                valid = True
        elif current == "REVIEWED":
            if target_status_clean in ("APPROVED", "DRAFT", "DEPRECATED"):
                valid = True
        elif current == "APPROVED":
            if target_status_clean in ("ACTIVE", "DEPRECATED"):
                valid = True
        elif current == "ACTIVE":
            if target_status_clean == "DEPRECATED":
                valid = True
        elif current == "DEPRECATED":
            if target_status_clean == "DRAFT":
                valid = True

        if not valid:
            raise ValueError(f"Invalid status transition from {current} to {target_status_clean}")

        card.status = target_status_clean
        card.updated_at = datetime.datetime.now(datetime.UTC).isoformat()

        if notes_clean:
            card.extra_metadata["review_notes"] = notes_clean
        if reason_clean:
            card.extra_metadata["status_change_reason"] = reason_clean

        if target_status_clean in ("APPROVED", "ACTIVE"):
            card.validation_state = "VALID"
        elif target_status_clean == "DEPRECATED" and "rejected" in reason_clean.lower():
            card.validation_state = "INVALID"

        self.db_manager.store_card(
            card,
            updater=updater_clean,
            reason=reason_clean or f"Transitioned status from {current} to {target_status_clean}"
        )
        return card

    def review_card(self, card_id: str, notes: str, updater: str = "reviewer") -> KnowledgeCard:
        """Promotes a card from DRAFT to REVIEWED securely."""
        return self.transition_status(card_id, "REVIEWED", updater=updater, reason="Card reviewed and staged for approval", notes=notes)

    def approve_card(self, card_id: str, updater: str = "approver") -> KnowledgeCard:
        """Promotes a card from REVIEWED to APPROVED securely."""
        return self.transition_status(card_id, "APPROVED", updater=updater, reason="Card approved by review gate")

    def activate_card(self, card_id: str, updater: str = "operator") -> KnowledgeCard:
        """Promotes a card from APPROVED to ACTIVE securely."""
        return self.transition_status(card_id, "ACTIVE", updater=updater, reason="Card promoted to active operational status")

    def reject_card(self, card_id: str, reason: str, updater: str = "reviewer") -> KnowledgeCard:
        """Rejects a card securely, marking it as DEPRECATED."""
        return self.transition_status(card_id, "DEPRECATED", updater=updater, reason=f"Rejected: {reason}")
