import pytest
from solomon_worker_orchestration import Task, SwarmOrchestrator, SwarmMemory, Architect, Planner

def test_hierarchy_scheduling():
    orchestrator = SwarmOrchestrator()
    task1 = Task("t1", "Build app", "Builder")
    task2 = Task("t2", "Design app", "Architect")

    orchestrator.add_task(task1)
    orchestrator.add_task(task2)
    orchestrator.execute_swarm()

    assert orchestrator.tasks["t1"].status == "COMPLETED"
    assert orchestrator.tasks["t2"].status == "COMPLETED"

def test_dependency_resolution():
    orchestrator = SwarmOrchestrator()
    task1 = Task("t1", "Design app", "Architect")
    task2 = Task("t2", "Plan app", "Planner", dependencies=["t1"])
    task3 = Task("t3", "Build app", "Builder", dependencies=["t2"])

    orchestrator.add_task(task3)
    orchestrator.add_task(task2)
    orchestrator.add_task(task1)

    orchestrator.execute_swarm()

    assert orchestrator.tasks["t1"].status == "COMPLETED"
    assert orchestrator.tasks["t2"].status == "COMPLETED"
    assert orchestrator.tasks["t3"].status == "COMPLETED"

def test_duplicate_prevention():
    orchestrator = SwarmOrchestrator()
    task1 = Task("t1", "Design app", "Architect")
    task2 = Task("t2", "Design app", "Architect")  # duplicate of t1

    orchestrator.add_task(task1)
    orchestrator.execute_swarm()
    assert orchestrator.tasks["t1"].status == "COMPLETED"

    orchestrator.add_task(task2)
    assert orchestrator.tasks["t2"].status == "COMPLETED" # should be skipped and marked complete immediately
    assert orchestrator.tasks["t2"].result == "Duplicate task result (cached)"
