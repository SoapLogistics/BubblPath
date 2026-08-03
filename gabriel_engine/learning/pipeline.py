from typing import Dict, Any, List
from gabriel_engine.learning.ingestion.ingestor import OutcomeIngestor
from gabriel_engine.learning.normalization.normalizer import OutcomeNormalizer
from gabriel_engine.learning.evidence.evidence_extractor import EvidenceExtractor
from gabriel_engine.learning.models import LearningRecord
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LearningPipeline:
    """
    The Evidence-Driven Gabriel Learning v2 Pipeline.
    """
    def __init__(self):
        self.ingestor = OutcomeIngestor()
        self.normalizer = OutcomeNormalizer()
        self.evidence_extractor = EvidenceExtractor()
        self.learning_records: Dict[str, LearningRecord] = {}

    def run_cycle(self) -> Dict[str, Any]:
        """
        Runs a complete learning cycle centered around LearningRecords.
        """
        pending = self.ingestor.get_pending_outcomes()
        results = {
            "ingested_count": len(pending),
            "evidence_extracted": 0,
            "learning_records_created": 0,
            "records_validated": 0
        }

        for raw_outcome in pending:
            try:
                # 1. Normalize
                normalized = self.normalizer.normalize(raw_outcome)

                # 2. Extract Evidence into Graph
                evidence_ids = self.evidence_extractor.process_normalized_outcome(normalized)
                results["evidence_extracted"] += len(evidence_ids)

                # 3. Create LearningRecord based on evidence
                if evidence_ids:
                    record_id = f"LR-{normalized.get('ingest_id')}"
                    evidence_payloads = [self.evidence_extractor.graph.nodes[eid] for eid in evidence_ids]

                    # Generate observations/hypothesis from evidence
                    success = normalized.get("success", False)
                    event_type = normalized.get("event_type", "unknown")

                    obs = f"Observed {'success' if success else 'failure'} in {event_type}"

                    hypothesis = {
                        "test": f"Hypothesis based on {obs}",
                        "expected": "Improved stability" if success else "Error prevention"
                    }

                    # Create procedure stub
                    procedure = {
                        "name": f"Procedure for {event_type}",
                        "action": "Do things successfully" if success else "Avoid doing this"
                    }

                    record = LearningRecord(
                        record_id=record_id,
                        evidence=evidence_payloads,
                        observations=[obs],
                        hypothesis=hypothesis,
                        procedure=procedure,
                        validation_status="VALIDATED" if success else "PENDING", # Dummy validation logic
                        confidence=0.8 if success else 0.3
                    )

                    self.learning_records[record_id] = record
                    results["learning_records_created"] += 1

                    if record.validation_status == "VALIDATED":
                        results["records_validated"] += 1
                        # In a full system, this validated record would be promoted to Mnemosyne here.

                # Mark as processed
                self.ingestor.mark_processed(raw_outcome["ingest_id"])

            except Exception as e:
                logger.error(f"Error processing outcome {raw_outcome.get('ingest_id')}: {e}")

        return results
