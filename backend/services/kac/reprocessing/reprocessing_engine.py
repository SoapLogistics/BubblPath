from typing import Dict, Any, List
import uuid

class ReprocessingEngine:
    def __init__(self, current_parser_version: str = "2.0", current_extraction_version: str = "2.0"):
        self.current_parser_version = current_parser_version
        self.current_extraction_version = current_extraction_version

    def evaluate_vault(self, vault_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a vault to see if reprocessing is justified based on version deltas.
        """
        parser_delta = float(self.current_parser_version) - float(vault_manifest.get("parser_version", "1.0"))
        extract_delta = float(self.current_extraction_version) - float(vault_manifest.get("extraction_version", "1.0"))

        expected_yield_gain = (parser_delta * 0.1) + (extract_delta * 0.15)

        priority = "LOW"
        if expected_yield_gain > 0.2:
            priority = "HIGH"
        elif expected_yield_gain > 0.1:
            priority = "MEDIUM"

        return {
            "reprocessing_job_id": str(uuid.uuid4()),
            "vault_id": vault_manifest.get("vault_id"),
            "expected_yield_gain": expected_yield_gain,
            "priority": priority,
            "status": "QUEUED" if priority in ["HIGH", "MEDIUM"] else "SKIPPED"
        }
