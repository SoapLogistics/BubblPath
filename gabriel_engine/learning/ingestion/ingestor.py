from typing import List, Dict, Any, Optional

class OutcomeIngestor:
    """
    Ingests raw outcome data from various sources (missions, tests, PRs, deployments)
    and normalizes them for the learning loop.
    """
    def __init__(self):
        self.raw_outcomes = []

    def ingest(self, source: str, raw_data: Dict[str, Any]) -> str:
        """
        Ingests a raw outcome.
        Returns an ingestion ID.
        """
        ingest_id = f"INGEST-{len(self.raw_outcomes) + 1}"
        record = {
            "ingest_id": ingest_id,
            "source": source,
            "raw_data": raw_data,
            "status": "PENDING"
        }
        self.raw_outcomes.append(record)
        return ingest_id

    def get_pending_outcomes(self) -> List[Dict[str, Any]]:
        return [o for o in self.raw_outcomes if o["status"] == "PENDING"]

    def mark_processed(self, ingest_id: str):
        for o in self.raw_outcomes:
            if o["ingest_id"] == ingest_id:
                o["status"] = "PROCESSED"
