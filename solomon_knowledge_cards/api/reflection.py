import datetime
from typing import Dict, Any, List, Optional
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.extractor.extractor import KnowledgeExtractor
from solomon_knowledge_cards.models.card import KnowledgeCard

class ReflectionEngine:
    def __init__(self, repository: CardRepository, learning_rate: float = 0.05):
        self.repository = repository
        self.learning_rate = learning_rate
        self.extractor = KnowledgeExtractor()

    def reinforce_confidence(self, task_outcome: str, associated_card_ids: List[str]) -> List[KnowledgeCard]:
        """
        Dynamically adjusts (reinforces) card confidence levels based on execution results.
        - Successful tasks increment the confidence of referenced remediation/skill cards (up to 1.0).
        - Failed tasks decrement the confidence of referenced remediation/skill cards (down to 0.0).
        """
        updated_cards = []
        is_success = task_outcome.lower() == "success"
        adjustment = self.learning_rate if is_success else -2 * self.learning_rate

        for card_id in associated_card_ids:
            card = self.repository.get_card(card_id)
            if card:
                old_conf = card.confidence
                # Bound between 0.0 and 1.0
                new_conf = max(0.0, min(1.0, old_conf + adjustment))
                if old_conf != new_conf:
                    card.confidence = round(new_conf, 3)
                    card.updated_at = datetime.datetime.now(datetime.UTC).isoformat()
                    reason = f"Reinforcement adjustment: {task_outcome.upper()} result changed confidence from {old_conf} to {card.confidence}"
                    self.repository.update_card(card, updater="reflection_engine", reason=reason)
                    updated_cards.append(card)

        return updated_cards

    def perform_self_reflection(self, worker_report: Dict[str, Any], ss3_review: Optional[Dict[str, Any]] = None) -> List[KnowledgeCard]:
        """
        Observes a worker execution report, synthesizes new candidate failure/repair/lesson cards,
        and links them back to their origin.
        """
        # Extract new draft cards
        draft_cards = self.extractor.extract_draft_cards(worker_report, ss3_review, creator="reflection_engine")

        # Save them into repository
        for card in draft_cards:
            self.repository.create_card(card, creator="reflection_engine", reason="Synthesized via background self-reflection")

        # Automatically adjust confidence of referenced parent checklists/skills
        procedure_id = worker_report.get("procedure_id")
        if procedure_id:
            outcome = worker_report.get("outcome", "unknown")
            self.reinforce_confidence(outcome, [procedure_id])

        return draft_cards
