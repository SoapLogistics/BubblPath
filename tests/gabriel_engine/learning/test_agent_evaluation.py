from gabriel_engine.learning.models import AgentPerformanceProfile
from gabriel_engine.learning.agent_evaluation.evaluator import AgentEvaluator

def test_agent_evaluator():
    profile = AgentPerformanceProfile(
        agent_id="jules",
        task_classes=["code_review", "refactoring"],
        success_rate=0.8,
        feedback_notes=[]
    )
    evaluator = AgentEvaluator()

    # Simulate success
    profile = evaluator.update_profile(profile, {"success": True, "ingest_id": "INGEST-1"})
    assert profile.success_rate == 0.81

    # Simulate failure
    profile = evaluator.update_profile(profile, {"success": False, "ingest_id": "INGEST-2"})
    assert profile.success_rate == 0.79
    assert len(profile.feedback_notes) == 1
    assert "INGEST-2" in profile.feedback_notes[0]
