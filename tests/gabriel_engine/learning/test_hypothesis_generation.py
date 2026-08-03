from gabriel_engine.learning.models import ProcedureCandidate
from gabriel_engine.learning.hypothesis_generation.generator import HypothesisGenerator

def test_hypothesis_generator():
    candidate = ProcedureCandidate(
        procedure_id="PROC-1",
        name="Test Procedure",
        applies_when={"condition": "test_env"},
        recommended_action=["Do something"],
        last_reviewed="2024-01-01"
    )
    generator = HypothesisGenerator()
    hypothesis = generator.generate_hypothesis(candidate)

    assert hypothesis["hypothesis_id"] == "HYP-PROC-1"
    assert hypothesis["procedure_id"] == "PROC-1"
    assert hypothesis["conditions"] == {"condition": "test_env"}
    assert "Test Procedure" in hypothesis["description"]
