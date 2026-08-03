from typing import Dict, Any, List
import logging

logger = logging.getLogger("gabriel_learning")

class MissionRecordIngester:
    """Ingests mission records and other operational ledger records into the Gabriel Learning pipeline."""
    def ingest(self, raw_outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Takes raw event dictionary traces and normalizes them for lesson extraction."""
        logger.info(f"Ingesting {len(raw_outcomes)} mission outcome records.")
        normalized = []
        for record in raw_outcomes:
            if "type" in record and record["type"] in ["mission_record", "test_outcome", "pr_review", "deployment", "human_feedback"]:
                normalized.append({
                    "id": record.get("id", "unknown"),
                    "source": record["type"],
                    "success": record.get("success", False),
                    "context": record.get("context", {}),
                    "agent": record.get("agent", "unknown")
                })
        return normalized
