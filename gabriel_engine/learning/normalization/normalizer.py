from typing import Dict, Any

class OutcomeNormalizer:
    """
    Normalizes raw ingested outcomes into a standard format for the learning pipeline.
    """
    def normalize(self, raw_outcome: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes an ingested record and returns a normalized format.
        """
        source = raw_outcome.get("source", "UNKNOWN")
        raw_data = raw_outcome.get("raw_data", {})

        normalized = {
            "ingest_id": raw_outcome.get("ingest_id"),
            "event_type": raw_data.get("event_type", source),
            "success": raw_data.get("success", False),
            "actors": raw_data.get("actors", []),
            "context": raw_data.get("context", {}),
            "metrics": raw_data.get("metrics", {})
        }

        return normalized
