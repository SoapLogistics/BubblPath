import pytest
from datetime import datetime
from backend.services.oswald.curriculum.models import GapEvidence, LearningObjective, CurriculumPlan, Prerequisite, StudyUnit, Assessment
from backend.services.oswald.curriculum.planner import CurriculumPlanner

def test_gap_inference():
    planner = CurriculumPlanner()
    evidence = [
        GapEvidence(source="eval_1", description="python async", confidence=0.4, importance=0.9),
        GapEvidence(source="eval_2", description="python async", confidence=0.5, importance=0.8),
        GapEvidence(source="eval_3", description="sql joins", confidence=0.8, importance=0.6)
    ]

    gaps = planner.infer_gaps(evidence)
    assert len(gaps) == 2

    # python async should have higher priority
    # (0.85 * 0.55 = 0.4675) vs sql joins (0.6 * 0.2 = 0.12)
    assert gaps[0]["description"] == "python async"
    assert gaps[1]["description"] == "sql joins"

def test_build_objectives():
    planner = CurriculumPlanner()
    gaps = [
        {"description": "python async", "priority": 0.5, "evidence_count": 2, "related_nodes": []},
        {"description": "sql joins", "priority": 0.2, "evidence_count": 1, "related_nodes": []}
    ]

    objectives = planner.build_objectives(gaps, seed=42)
    assert len(objectives) == 2
    assert objectives[0].title == "Master python async"
    assert objectives[0].priority_score == 5.0
    assert len(objectives[0].study_units) == 1

def test_sequence_circular_dependency():
    planner = CurriculumPlanner()
    obj1 = LearningObjective(
        id="obj1", title="Obj 1", description="",
        assessment=Assessment(method="quiz", passing_score=0.8, description=""),
        stop_condition="",
        prerequisites=[Prerequisite(objective_id="obj2")]
    )
    obj2 = LearningObjective(
        id="obj2", title="Obj 2", description="",
        assessment=Assessment(method="quiz", passing_score=0.8, description=""),
        stop_condition="",
        prerequisites=[Prerequisite(objective_id="obj1")]
    )

    with pytest.raises(ValueError, match="Circular dependencies detected"):
        planner.sequence([obj1, obj2], budget=10.0)

def test_sequence_budget():
    planner = CurriculumPlanner()
    # Create 3 objectives, cost 1.0 each, total budget 2.0
    objs = []
    for i in range(3):
        unit = StudyUnit(title=f"Unit {i}", description="", estimated_cost=1.0, unit_type="knowledge")
        obj = LearningObjective(
            id=f"obj{i}", title=f"Obj {i}", description="", priority_score=float(i), # obj2 has highest priority
            assessment=Assessment(method="quiz", passing_score=0.8, description=""),
            stop_condition="",
            study_units=[unit]
        )
        objs.append(obj)

    plan = planner.sequence(objs, budget=2.5)
    assert len(plan.objectives) == 2
    assert plan.consumed_budget == 2.0
    # Highest priority should be selected (obj2, obj1)
    assert set(o.id for o in plan.objectives) == {"obj2", "obj1"}

def test_revise_plan():
    planner = CurriculumPlanner()
    obj1 = LearningObjective(
        id="obj1", title="Obj 1", description="", priority_score=1.0,
        assessment=Assessment(method="quiz", passing_score=0.8, description=""),
        stop_condition=""
    )
    plan = CurriculumPlan(objectives=[obj1], budget=10.0)

    # Assess pass
    results = {"obj1": {"score": 0.9}}
    revised = planner.revise(plan, results)
    assert revised.objectives[0].status == "completed"

    # Assess fail
    plan.objectives[0].status = "pending"
    results = {"obj1": {"score": 0.5}}
    revised = planner.revise(plan, results)
    assert revised.objectives[0].status == "failed"
    assert revised.objectives[0].priority_score > 1.0
