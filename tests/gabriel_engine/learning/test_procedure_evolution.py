from gabriel_engine.learning.models import ProcedureCandidate
from gabriel_engine.learning.procedure_evolution.evolver import ProcedureEvolver

def test_procedure_evolver():
    candidate = ProcedureCandidate(
        procedure_id="PROC-1",
        name="Test Procedure",
        applies_when={},
        recommended_action=[],
        supporting_outcomes=1,
        contradicting_outcomes=0,
        confidence=0.5,
        last_reviewed="2024-01-01"
    )

    evolver = ProcedureEvolver()

    # Success evidence
    candidate = evolver.evolve(candidate, {"success": True, "ingest_id": "INGEST-1"})
    assert candidate.supporting_outcomes == 2
    assert candidate.confidence == 0.55
    assert "INGEST-1" in candidate.evidence_ids

    # Failure evidence
    candidate = evolver.evolve(candidate, {"success": False, "ingest_id": "INGEST-2"})
    assert candidate.contradicting_outcomes == 1
    assert candidate.confidence == 0.45
    assert "INGEST-2" in candidate.evidence_ids
