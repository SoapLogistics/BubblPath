from gabriel_engine.learning.models import ProcedureCandidate
from datetime import datetime

def test_procedure_candidate_model():
    data = {
        "procedure_id": "PROC-CODE-REVIEW-0042",
        "name": "Architectural review routing",
        "applies_when": {
            "task_type": "cross-module architectural change",
            "files_changed_minimum": 10
        },
        "recommended_action": [
            "Assign implementation to Jules",
            "Assign architecture review to Claude",
            "Require integration tests before merge"
        ],
        "supporting_outcomes": 14,
        "contradicting_outcomes": 2,
        "success_rate_before": 0.64,
        "success_rate_after": 0.87,
        "confidence": 0.82,
        "status": "VALIDATED",
        "last_reviewed": "2026-08-03",
        "evidence_ids": [
            "MISSION-142",
            "PR-38",
            "AUDIT-2026-08-03"
        ]
    }
    candidate = ProcedureCandidate(**data)
    assert candidate.procedure_id == "PROC-CODE-REVIEW-0042"
    assert candidate.name == "Architectural review routing"
    assert candidate.status == "VALIDATED"
