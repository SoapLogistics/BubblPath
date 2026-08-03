from typing import Dict, Any, List
from gabriel_engine.learning.models import ProcedureCandidate

class ProcedureEvolver:
    """
    Evaluates historical procedures and evolves them based on new evidence.
    """
    def evolve(self, candidate: ProcedureCandidate, new_evidence: Dict[str, Any]) -> ProcedureCandidate:
        """
        Evolves an existing procedure candidate with new evidence.
        """
        if new_evidence.get("success"):
            candidate.supporting_outcomes += 1
            # Adjust confidence up
            candidate.confidence = round(min(1.0, candidate.confidence + 0.05), 2)
        else:
            candidate.contradicting_outcomes += 1
            # Adjust confidence down
            candidate.confidence = round(max(0.0, candidate.confidence - 0.1), 2)

        candidate.evidence_ids.append(str(new_evidence.get("ingest_id", "UNKNOWN")))
        return candidate
