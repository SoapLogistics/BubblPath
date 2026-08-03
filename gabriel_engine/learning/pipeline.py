import json
import hashlib
import uuid
import datetime
from typing import Dict, Any, List, Optional
import logging

from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from gabriel_engine.learning.models import LearningRecord

logger = logging.getLogger(__name__)

class LearningRepository:
    """Wraps DatabaseManager to provide persistence for LearningRecords as KnowledgeCards."""
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_record(self, record: LearningRecord) -> None:
        """Saves a LearningRecord to the database as a KnowledgeCard of type LESSON."""

        # Convert LearningRecord to KnowledgeCard
        # Storing fields specific to LearningRecord in extra_metadata
        extra_metadata = {
            "learning_record": True,
            "mission_id": record.mission_id,
            "objective": record.objective,
            "outcome": record.outcome,
            "agent": record.agent,
            "supporting_evidence": record.supporting_evidence,
            "contradicting_evidence": record.contradicting_evidence,
            "procedure_id": record.procedure_id,
            "checksum": record.checksum,
            "status": record.status
        }

        # Determine KnowledgeCard status based on LearningRecord status
        status_map = {
            "CANDIDATE": "DRAFT",
            "VALIDATED": "REVIEWED",
            "ACTIVE": "ACTIVE",
            "DEGRADED": "DEPRECATED",
            "RETIRED": "DEPRECATED",
            "REJECTED": "DEPRECATED"
        }
        card_status = status_map.get(record.status, "DRAFT")

        card = KnowledgeCard(
            card_id=record.id,
            card_type="LESSON",
            schema_version="2.0",
            title=f"Learning Record: {record.procedure_id}",
            summary=f"Learned procedure {record.procedure_id} from {record.agent} with outcome {record.outcome}",
            body=f"Objective: {record.objective}\nOutcome: {record.outcome}\nStatus: {record.status}",
            status=card_status,
            confidence=record.confidence,
            validation_state="VALID" if record.status in ("VALIDATED", "ACTIVE") else "UNVALIDATED",
            created_at=record.timestamp,
            updated_at=datetime.datetime.now(datetime.UTC).isoformat(),
            created_by=record.agent,
            source_type="GabrielPerpetualLoop",
            source_ids=[record.mission_id] if record.mission_id else [],
            parent_card_ids=[],
            related_card_ids=[],
            tags=["learning_record", record.procedure_id],
            security_classification="INTERNAL",
            evidence=json.dumps({"supporting": record.supporting_evidence, "contradicting": record.contradicting_evidence}),
            extra_metadata=extra_metadata
        )

        try:
            self.db_manager.store_card(card, updater="GabrielLearningPipeline", reason=f"Saved LearningRecord {record.id}")
        except Exception as e:
            logger.error(f"Failed to save LearningRecord {record.id}: {e}")

    def get_record_by_procedure_id(self, procedure_id: str) -> Optional[LearningRecord]:
        """Retrieves a LearningRecord from the database by its procedure ID."""
        cards = self.db_manager.list_all_cards()
        for card in cards:
            if card.card_type == "LESSON" and card.extra_metadata.get("learning_record") and card.extra_metadata.get("procedure_id") == procedure_id:
                return self._card_to_record(card)
        return None

    def _card_to_record(self, card: KnowledgeCard) -> LearningRecord:
        """Converts a KnowledgeCard back to a LearningRecord."""
        meta = card.extra_metadata
        return LearningRecord(
            id=card.card_id,
            mission_id=meta.get("mission_id"),
            objective=meta.get("objective"),
            outcome=meta.get("outcome"),
            agent=meta.get("agent"),
            timestamp=card.created_at,
            supporting_evidence=meta.get("supporting_evidence", []),
            contradicting_evidence=meta.get("contradicting_evidence", []),
            confidence=card.confidence,
            procedure_id=meta.get("procedure_id"),
            status=meta.get("status"),
            checksum=meta.get("checksum")
        )

class GabrielLearningPipeline:
    def __init__(self, db_manager: DatabaseManager):
        self.repository = LearningRepository(db_manager)

    def process_assimilation_result(self, project_name: str, assimilation_details: List[Dict[str, Any]], loop_log: Dict[str, Any]) -> List[LearningRecord]:
        """
        Parses GabrielPerpetualLoop STAGE 10 outputs and returns fully formed LearningRecords.
        Also handles basic deduplication and contradiction detection.
        """
        records = []
        for detail in assimilation_details:
            capability_name = detail.get("capability_name", "unknown")
            action = detail.get("chosen_action", "UNKNOWN")

            # Simple outcome determination
            if action in ["REIMPLEMENT", "INTEGRATE", "WRAP"]:
                if detail.get("fold_into_self_status", "").startswith("FAILED"):
                    outcome = "FAILURE"
                else:
                    outcome = "SUCCESS"
            else:
                outcome = "SKIPPED"

            if outcome == "SKIPPED":
                continue

            # Construct evidence string
            evidence_str = json.dumps({
                "action": action,
                "score": detail.get("utility_score"),
                "status": detail.get("fold_into_self_status"),
                "report": detail.get("crucible_report", {})
            })

            # Calculate checksum for deduplication
            checksum_input = f"{project_name}_{capability_name}_{action}_{outcome}".encode('utf-8')
            checksum = hashlib.sha256(checksum_input).hexdigest()

            # Deduplication & Contradiction check
            existing_record = self.repository.get_record_by_procedure_id(capability_name)

            if existing_record:
                # Contradiction: same procedure, different outcome
                if existing_record.outcome != outcome:
                    logger.info(f"Contradiction detected for {capability_name}. Previous outcome: {existing_record.outcome}, New outcome: {outcome}")
                    new_confidence = max(0.0, existing_record.confidence - 0.2)
                    new_status = "DEGRADED" if new_confidence < 0.5 else existing_record.status

                    updated_record = existing_record.model_copy(update={
                        "confidence": new_confidence,
                        "status": new_status,
                        "contradicting_evidence": existing_record.contradicting_evidence + [evidence_str],
                        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
                    })
                    self.repository.save_record(updated_record)
                    records.append(updated_record)
                else:
                    # Supporting evidence
                    new_confidence = min(1.0, existing_record.confidence + 0.1)
                    new_status = "ACTIVE" if new_confidence >= 0.8 else existing_record.status

                    updated_record = existing_record.model_copy(update={
                        "confidence": new_confidence,
                        "status": new_status,
                        "supporting_evidence": existing_record.supporting_evidence + [evidence_str],
                        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
                    })
                    self.repository.save_record(updated_record)
                    records.append(updated_record)
            else:
                # New record
                new_record = LearningRecord(
                    id=f"LR-{uuid.uuid4().hex[:8].upper()}",
                    mission_id=loop_log.get("project_name", project_name),
                    objective=f"Assimilate capability {capability_name}",
                    outcome=outcome,
                    agent="GabrielPerpetualLoop",
                    supporting_evidence=[evidence_str],
                    contradicting_evidence=[],
                    confidence=0.5 if outcome == "SUCCESS" else 0.1,
                    procedure_id=capability_name,
                    status="CANDIDATE",
                    checksum=checksum
                )
                self.repository.save_record(new_record)
                records.append(new_record)

        return records
