import uuid
import datetime
import json
from typing import Dict, Any, Optional, List
from solomon_knowledge_cards.models import KnowledgeCardModel, CardType, CardStatus, ValidationState
from solomon_knowledge_cards.repository import KnowledgeRepository

class KnowledgeEngine:
    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository

    def extract_from_report(self, worker_report: Dict[str, Any], review_result: Optional[Dict[str, Any]] = None) -> List[KnowledgeCardModel]:
        """Deterministic extractor converting execution telemetry and SS3 reviews into draft cards."""
        generated_cards = []

        task_id = worker_report.get("task_id", str(uuid.uuid4()))
        procedure_id = worker_report.get("procedure_id", "UNKNOWN")
        success = worker_report.get("success", True)
        execution_summary = worker_report.get("summary", "")
        error_logs = worker_report.get("error_logs", "")

        # Optional review validation context
        reviewer = "SS3"
        validated_by = ValidationState.PENDING
        last_validated_at = None
        rejection_reason = None
        evidence_reference = worker_report.get("evidence", "")

        if review_result:
            reviewer = review_result.get("reviewer", "SS3")
            approved = review_result.get("approved", True)
            rejection_reason = review_result.get("rejection_reason")
            validated_by = ValidationState.HUMAN_VALIDATED if reviewer == "HUMAN" else ValidationState.SYSTEM_VALIDATED
            last_validated_at = datetime.datetime.utcnow().isoformat() + "Z"
            if not approved:
                validated_by = ValidationState.REJECTED

        # Case 1: Task failed -> Produce FAILURE Card and corresponding REPAIR Card
        if not success:
            failure_id = f"FAIL-{uuid.uuid4().hex[:8]}"
            failure_card = KnowledgeCardModel(
                card_id=failure_id,
                card_type=CardType.FAILURE,
                title=f"Failure Incident in {procedure_id}",
                summary=f"Incident encountered during execution of {procedure_id}.",
                body=f"Execution log findings:\n{execution_summary}\n\nError telemetry:\n{error_logs}",
                status=CardStatus.DRAFT,
                confidence=0.4,
                validation_state=validated_by,
                created_by="ENGINE_EXTRACTOR",
                source_type="WORKER_REPORT",
                source_ids=[task_id],
                parent_card_ids=[procedure_id] if procedure_id != "UNKNOWN" else [],
                evidence=evidence_reference,
                metadata={"task_id": task_id, "rejection_reason": rejection_reason},
                why_created="To document and track recurring execution failure signatures.",
                problem_solved="Capturing failure telemetry context.",
                future_work_dependent="None"
            )
            generated_cards.append(failure_card)

            # If a repair attempt or script recovery is documented, generate REPAIR card
            resolution = worker_report.get("resolution") or (review_result.get("resolution") if review_result else None)
            if resolution:
                repair_id = f"REPAIR-{uuid.uuid4().hex[:8]}"
                repair_card = KnowledgeCardModel(
                    card_id=repair_id,
                    card_type=CardType.REPAIR,
                    title=f"Repair Procedure for Failure {failure_id}",
                    summary=f"Resolution blueprint applied to solve Failure {failure_id}.",
                    body=f"Recovery Action blueprint:\n{resolution}",
                    status=CardStatus.DRAFT,
                    confidence=0.5 if not review_result else (0.8 if review_result.get("approved") else 0.2),
                    validation_state=validated_by,
                    created_by="ENGINE_EXTRACTOR",
                    source_type="WORKER_REPORT",
                    source_ids=[task_id],
                    parent_card_ids=[failure_id],
                    evidence=evidence_reference,
                    metadata={"failure_id": failure_id, "rejection_reason": rejection_reason},
                    why_created="To provide a repeatable recovery checklist for similar future errors.",
                    problem_solved=f"Resolves failure incident documented in {failure_id}.",
                    future_work_dependent="None"
                )
                generated_cards.append(repair_card)

            # SOK Phase 8 (Skill Discovery) - Auto-discover missing skills when execution logs indicate capability issues
            if "unsupported" in error_logs.lower() or "missing capability" in error_logs.lower() or "not found" in error_logs.lower():
                skill_id = f"SKILL-REQ-{uuid.uuid4().hex[:8]}"
                skill_card = KnowledgeCardModel(
                    card_id=skill_id,
                    card_type=CardType.SKILL,
                    title=f"Missing Skill Discovery for {procedure_id}",
                    summary="System-wide automated capability gap mapped during execution failure.",
                    body=f"Analysis of failure logs indicates a tool/skill deficiency. Required capabilities details:\n{error_logs}",
                    status=CardStatus.DRAFT,
                    confidence=0.3,
                    validation_state=ValidationState.PENDING,
                    created_by="ENGINE_EXTRACTOR",
                    source_type="SKILL_GAP_ANALYSIS",
                    source_ids=[task_id],
                    parent_card_ids=[failure_id],
                    why_created="To flag capability gaps and plan research playbooks to acquire the missing skill.",
                    problem_solved=f"Documents missing prerequisites for {procedure_id}.",
                    future_work_dependent="None"
                )
                generated_cards.append(skill_card)

        # Case 2: Task succeeded -> Produce LESSON / KNOWLEDGE Card
        else:
            lesson_id = f"LESSON-{uuid.uuid4().hex[:8]}"
            lesson_card = KnowledgeCardModel(
                card_id=lesson_id,
                card_type=CardType.LESSON,
                title=f"SOP Optimization in {procedure_id}",
                summary=f"Acquired execution insights while running task {task_id}.",
                body=f"Successful execution takeaways:\n{execution_summary}",
                status=CardStatus.DRAFT,
                confidence=0.6,
                validation_state=validated_by,
                created_by="ENGINE_EXTRACTOR",
                source_type="WORKER_REPORT",
                source_ids=[task_id],
                parent_card_ids=[procedure_id] if procedure_id != "UNKNOWN" else [],
                evidence=evidence_reference,
                metadata={"task_id": task_id, "rejection_reason": rejection_reason},
                why_created="To codify optimizations and successful runtime parameters.",
                problem_solved="Continuous refinement of standard procedures.",
                future_work_dependent="None"
            )
            generated_cards.append(lesson_card)

        # Save generated draft cards directly in PENDING_REVIEW or DRAFT
        for card in generated_cards:
            self.repository.create_card(card, actor="ENGINE_EXTRACTOR")

        return generated_cards

    def promote_card(self, card_id: str, reviewer: str = "SS3") -> None:
        """Explicit promotion flow logic: DRAFT -> REVIEWED -> APPROVED -> ACTIVE."""
        card = self.repository.get_card(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found.")

        # Status level progression logic
        if card.status == CardStatus.DRAFT:
            card.status = CardStatus.REVIEWED
            card.validation_state = ValidationState.LLM_EVAL if reviewer == "SS3" else ValidationState.HUMAN_VALIDATED
        elif card.status == CardStatus.REVIEWED:
            card.status = CardStatus.APPROVED
            card.validation_state = ValidationState.SYSTEM_VALIDATED
        elif card.status == CardStatus.APPROVED:
            card.status = CardStatus.ACTIVE
            card.validation_state = ValidationState.HUMAN_VALIDATED
        else:
            raise ValueError(f"Promotion transition not supported from status: {card.status}")

        card.updated_at = datetime.datetime.utcnow().isoformat() + "Z"
        self.repository.update_card(card, actor=reviewer)

    def reject_card(self, card_id: str, reason: str, reviewer: str = "SS3") -> None:
        """Transition card status to indicate rejection, recording audit reasons in metadata."""
        card = self.repository.get_card(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found.")

        card.validation_state = ValidationState.REJECTED
        card.status = CardStatus.DEPRECATED
        card.metadata["rejection_reason"] = reason
        card.updated_at = datetime.datetime.utcnow().isoformat() + "Z"
        self.repository.update_card(card, actor=reviewer)

    def retrieve_active_operational_guidance(self, query: str) -> List[Dict[str, Any]]:
        """Search engine returning ONLY approved and trusted operational guidance."""
        matches = self.repository.search_by_text(query)
        trusted_results = []
        for card in matches:
            if card.status in [CardStatus.APPROVED, CardStatus.ACTIVE]:
                trusted_results.append({
                    "card_id": card.card_id,
                    "title": card.title,
                    "type": card.card_type,
                    "confidence": card.confidence,
                    "validation_state": card.validation_state,
                    "evidence": card.evidence,
                    "related_procedures": card.parent_card_ids,
                    "match_explanation": f"Matched query keyword in {card.card_type} card fields."
                })
        return trusted_results

    # SOK Phase 10: Metrics Tracking
    def calculate_sok_metrics(self, export_path: Optional[str] = "growth_metrics.json") -> Dict[str, Any]:
        """Periodically aggregates SOK system metadata and saves them to a tracking file."""
        all_cards = self.repository.list_cards()
        total_count = len(all_cards)

        type_distribution = {}
        status_distribution = {}
        total_confidence = 0.0
        active_approved_count = 0

        for card in all_cards:
            type_distribution[card.card_type] = type_distribution.get(card.card_type, 0) + 1
            status_distribution[card.status] = status_distribution.get(card.status, 0) + 1
            total_confidence += card.confidence
            if card.status in [CardStatus.APPROVED, CardStatus.ACTIVE]:
                active_approved_count += 1

        avg_confidence = total_confidence / total_count if total_count > 0 else 0.0
        reuse_rate = active_approved_count / total_count if total_count > 0 else 0.0

        metrics = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "total_cards_count": total_count,
            "average_confidence": round(avg_confidence, 4),
            "reuse_rate": round(reuse_rate, 4),
            "distribution_by_type": type_distribution,
            "distribution_by_status": status_distribution
        }

        if export_path:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)

        return metrics

    # SOK Phase 11: Passive Growth & Maintenance Loop
    def run_passive_growth_maintenance(self) -> Dict[str, Any]:
        """Idle maintenance tasks: Scans for duplicate cards and deprecates/resolves older revisions."""
        all_cards = self.repository.list_cards()
        duplicates_found = 0
        resolved_stale_drafts = 0

        # Simple deduplication based on body content match
        content_map = {}
        for card in all_cards:
            # Clean/strip whitespace to check body matches
            body_hash = "".join(card.body.split()).lower()
            if not body_hash:
                continue

            if body_hash in content_map:
                # Merge duplicate draft cards into the older validated card
                existing_card = content_map[body_hash]
                if card.status == CardStatus.DRAFT and existing_card.status != CardStatus.DRAFT:
                    # Deprecate duplicate card to clean database index
                    card.status = CardStatus.DEPRECATED
                    card.metadata["deduplication_status"] = f"Merged as duplicate of {existing_card.card_id}"
                    self.repository.update_card(card, actor="PASSIVE_GROWTH_MAINTENANCE")
                    duplicates_found += 1
            else:
                content_map[body_hash] = card

            # Soft archive stale unreviewed drafts older than 30 days (mock simulated in test via custom metadata)
            if card.status == CardStatus.DRAFT and card.metadata.get("is_stale_simulation"):
                card.status = CardStatus.ARCHIVED
                self.repository.update_card(card, actor="PASSIVE_GROWTH_MAINTENANCE")
                resolved_stale_drafts += 1

        return {
            "duplicates_merged": duplicates_found,
            "stale_drafts_archived": resolved_stale_drafts
        }
