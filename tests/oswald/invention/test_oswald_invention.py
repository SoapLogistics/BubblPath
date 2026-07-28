import pytest
from backend.services.oswald.invention.problem_registry import ProblemRecord
from backend.services.oswald.invention.invention_manager import InventionManager
from backend.services.oswald.laboratory.hypothesis_manager import HypothesisCard

def test_invention_generation():
    manager = InventionManager()

    problem = ProblemRecord(problem_id="p1", title="Memory Leak in Planner", description="OOM error during deep graph search", domain="Memory", source="Telemetry")
    cross_domain = ["Garbage Collection (OS)", "Graph Sparsification (Math)"]

    invention = manager.generate_candidate(problem, cross_domain)

    assert invention.novelty_status == "NEW_COMBINATION"
    assert "Garbage Collection" in invention.summary
    assert problem.problem_id in invention.problem_ids

    hypothesis = manager.convert_to_hypothesis(invention)

    assert isinstance(hypothesis, HypothesisCard)
    assert hypothesis.subsystem == invention.title
