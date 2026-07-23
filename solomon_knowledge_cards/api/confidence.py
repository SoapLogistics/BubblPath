import time
import datetime
from typing import List, Optional
from ..storage.db import DatabaseManager
from .repository import CardRepository

class ConfidenceEngine:
    def __init__(self, db_manager: DatabaseManager, repository: CardRepository):
        self.db_manager = db_manager
        self.repository = repository

        # Hyperparameters for confidence updates
        self.SUCCESS_INCREMENT = 0.05
        self.FAILURE_DECREMENT = 0.10
        self.MAX_CONFIDENCE = 1.0
        self.MIN_CONFIDENCE = 0.1

    def record_success(self, card_id: str, updater: str = "confidence_engine") -> float:
        """Increases the confidence score of a card after a successful application."""
        card = self.repository.get_card(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found.")

        new_confidence = min(card.confidence + self.SUCCESS_INCREMENT, self.MAX_CONFIDENCE)
        self._update_confidence(card_id, new_confidence, updater, "Success registered.")
        return new_confidence

    def record_failure(self, card_id: str, updater: str = "confidence_engine") -> float:
        """Decreases the confidence score of a card after a failure."""
        card = self.repository.get_card(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found.")

        new_confidence = max(card.confidence - self.FAILURE_DECREMENT, self.MIN_CONFIDENCE)
        self._update_confidence(card_id, new_confidence, updater, "Failure registered.")
        return new_confidence

    def _update_confidence(self, card_id: str, new_confidence: float, updater: str, reason: str):
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE knowledge_cards
                SET confidence = ?, updated_at = CURRENT_TIMESTAMP
                WHERE card_id = ?
            ''', (new_confidence, card_id))

            # Log the revision
            cursor.execute('''
                INSERT INTO revisions (card_id, field_changed, old_value, new_value, changed_by, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (card_id, "confidence", None, str(new_confidence), updater, reason))

    def generate_repair_from_traceback(self, traceback_str: str, failed_task_id: str, creator: str = "confidence_engine") -> str:
        """Parses a traceback and generates a draft REPAIR or FAILURE card."""
        # Simple extraction logic. In a full implementation this would call an LLM.
        lines = traceback_str.strip().split("\n")
        error_msg = lines[-1] if lines else "Unknown error"

        card_data = {
            "card_id": f"FC-{int(time.time())}",
            "card_type": "FAILURE",
            "schema_version": "1.0",
            "title": f"Automated Failure Report: {error_msg[:50]}",
            "summary": f"Task {failed_task_id} failed with error: {error_msg}",
            "body": f"```\n{traceback_str}\n```",
            "status": "DRAFT",
            "confidence": 0.5,
            "validation_state": "UNVALIDATED",
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "created_by": creator,
            "source_type": "automated_traceback",
            "source_ids": [failed_task_id],
            "parent_card_ids": [],
            "related_card_ids": [],
            "tags": ["automated", "failure"],
            "security_classification": "INTERNAL",
            "evidence": "Generated from traceback log.",
            "why_created": "To track a runtime failure automatically.",
            "problem_solved": "N/A",
            "future_work_dependent": "Needs repair."
        }

        from ..models.card import KnowledgeCard
        import time
        import datetime

        card = KnowledgeCard.from_dict(card_data)
        self.repository.create_card(card, creator=creator, reason="Automated traceback ingestion.")
        return card.card_id
