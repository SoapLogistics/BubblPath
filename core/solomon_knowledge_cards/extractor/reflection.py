import datetime
import uuid
from typing import List, Dict, Optional
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.models.card import KnowledgeCard

class ReflectionSynthesizer:
    def __init__(self, repository: CardRepository):
        self.repository = repository

    def analyze_failures_and_synthesize_research(self) -> List[KnowledgeCard]:
        """
        Scans all failure and repair cards in the repository, clusters them by common keywords/tags,
        and generates new RESEARCH cards for high-frequency failure modes that need investigation.
        """
        all_cards = self.repository.list_cards()
        failures = [c for c in all_cards if c.card_type == "FAILURE"]


        # Cluster by tags or keywords
        keyword_counts: Dict[str, List[str]] = {}
        # Keywords to scan for
        target_keywords = ["timeout", "docker", "port", "pip", "api", "database", "memory"]

        for fail in failures:
            combined_text = f"{fail.title} {fail.summary} {fail.body}".lower()
            for kw in target_keywords:
                if kw in combined_text:
                    if kw not in keyword_counts:
                        keyword_counts[kw] = []
                    keyword_counts[kw].append(fail.card_id)

        synthesized_cards = []
        now_str = datetime.datetime.now(datetime.UTC).isoformat()

        # Generate research objective for any keyword having >= 2 failures
        for kw, fail_ids in keyword_counts.items():
            if len(fail_ids) >= 2:
                research_id = f"RS-{uuid.uuid4().hex[:8].upper()}"

                # Check if a research card for this keyword already exists to prevent duplicate research cards
                existing_research = [c for c in all_cards if c.card_type == "RESEARCH" and kw in c.tags]
                if existing_research:
                    continue

                title = f"Research: Optimize {kw.capitalize()} handling and robustness"
                summary = f"Autonomous research objective synthesized due to {len(fail_ids)} separate failures related to '{kw}'."

                body = (
                    f"### Research Objective\n"
                    f"**Focus Area:** `{kw.capitalize()} Operations`\n"
                    f"**Triggering Failures:** {', '.join(fail_ids)}\n\n"
                    f"**Problem Statement:**\n"
                    f"Multiple worker operations have hit failures related to '{kw}'. We need to investigate and draft a generalized repair strategy to prevent recurring timeouts or binding blocks.\n\n"
                    f"**Status:** `Needs Investigation`"
                )

                research_card = KnowledgeCard(
                    card_id=research_id,
                    card_type="RESEARCH",
                    schema_version="1.0.0",
                    title=title,
                    summary=summary,
                    body=body,
                    status="DRAFT",
                    confidence=0.5,
                    validation_state="UNVALIDATED",
                    created_at=now_str,
                    updated_at=now_str,
                    created_by="reflection_synthesizer",
                    source_type="SYSTEM_REFLECTION",
                    source_ids=fail_ids,
                    parent_card_ids=[],
                    related_card_ids=fail_ids,
                    tags=["research", "reflection", "investigation", kw],
                    security_classification="INTERNAL",
                    evidence=f"Synthesized from historical failure records: {fail_ids}",
                    why_created=f"To investigate and systematically resolve recurring failure patterns around '{kw}'.",
                    problem_solved=f"Structures active study targets for {len(fail_ids)} unresolved errors.",
                    future_work_dependent="Outcome of this research will drive the creation of new SKILL and REPAIR playbooks."
                )

                self.repository.create_card(research_card, creator="reflection_synthesizer", reason="Synthesized from recurring failure analysis")
                synthesized_cards.append(research_card)

        return synthesized_cards

    def apply_reinforcement_feedback(
        self,
        card_id: str,
        was_successful: bool,
        operator: str = "feedback_engine"
    ) -> Optional[KnowledgeCard]:
        """
        Increments or decrements a card's confidence score based on worker execution outcomes.
        - If was_successful = True: Increments confidence by +0.05 (clamped to 1.0).
        - If was_successful = False: Decrements confidence by -0.10 (clamped to 0.0).
        - If confidence falls below 0.30, flags validation_state as UNVALIDATED.
        """
        card = self.repository.get_card(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found.")

        old_confidence = card.confidence

        if was_successful:
            new_confidence = min(1.0, old_confidence + 0.05)
            action_str = f"Reinforced confidence: {old_confidence:.2f} -> {new_confidence:.2f} (Success Outcome)"
        else:
            new_confidence = max(0.0, old_confidence - 0.10)
            action_str = f"Decayed confidence: {old_confidence:.2f} -> {new_confidence:.2f} (Failure Outcome)"

        card.confidence = round(new_confidence, 3)
        card.updated_at = datetime.datetime.now(datetime.UTC).isoformat()

        # Dynamic demotion threshold
        if card.confidence < 0.30 and card.validation_state == "VALID":
            card.validation_state = "UNVALIDATED"
            card.status = "DRAFT"
            action_str += " | DEMOTED to DRAFT/UNVALIDATED due to low confidence threshold (<0.3)"

        self.repository.db_manager.store_card(
            card,
            updater=operator,
            reason=action_str
        )
        return card
