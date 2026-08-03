import pytest
from gabriel_engine.learning.mission_loop import MissionOutcomeLearningLoop

def test_mission_learning_loop():
    loop = MissionOutcomeLearningLoop()
    events = [
        {"type": "test_outcome", "success": False, "context": {"task_type": "refactor"}, "agent": "Jules"},
        {"type": "pr_review", "success": True, "context": {"task_type": "architecture"}, "agent": "Claude"}
    ]
    results = loop.execute_loop(events)

    assert len(results["failure_prevention_rules"]) == 1
    assert len(results["agent_performance_profiles"]) == 1

    assert results["failure_prevention_rules"][0]["trigger"] == "refactor"
    assert results["agent_performance_profiles"][0]["agent"] == "Claude"
