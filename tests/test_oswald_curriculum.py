import pytest
import datetime
from backend.services.oswald.curriculum_models import (
    GapEvidence, EvidenceType, Capability, Prerequisite,
    LearningObjective, StudyUnit, Assessment, CurriculumPlan
)
from backend.services.oswald.curriculum_generator import (
    infer_gaps, build_objectives, sequence, revise, explain
)

def test_gap_deduplication():
    # Repeated failures on the same capability
    evidence = [
        GapEvidence("1", EvidenceType.TASK_FAILURE, "cap_1", "2023-01-01T10:00:00", {}, 5.0, 1),
        GapEvidence("2", EvidenceType.TASK_FAILURE, "cap_1", "2023-01-02T10:00:00", {"error": "timeout"}, 8.0, 1),
        GapEvidence("3", EvidenceType.MISSING_NODE, "cap_2", "2023-01-01T10:00:00", {}, 10.0, 1),
    ]

    gaps = infer_gaps(evidence)

    assert len(gaps) == 2

    cap1_gap = next(g for g in gaps if g.source_identifier == "cap_1")
    assert cap1_gap.recurrence_count == 2
    assert cap1_gap.impact_score == 8.0
    assert cap1_gap.timestamp == "2023-01-02T10:00:00"

def test_circular_prerequisites():
    obj1 = LearningObjective("1", "cap_A", "reason", 10.0, 10.0, "art", "stop",
                             [Prerequisite("cap_B", True)], [], Assessment("a", "crit", 0.8, "test"))
    obj2 = LearningObjective("2", "cap_B", "reason", 10.0, 10.0, "art", "stop",
                             [Prerequisite("cap_C", True)], [], Assessment("a", "crit", 0.8, "test"))
    obj3 = LearningObjective("3", "cap_C", "reason", 10.0, 10.0, "art", "stop",
                             [Prerequisite("cap_A", True)], [], Assessment("a", "crit", 0.8, "test"))

    plan = sequence([obj1, obj2, obj3], {}, 100.0)

    assert plan.status == "FAILED"
    assert len(plan.cycles_detected) > 0
    assert "Cycle detected" in plan.repair_proposal

def test_zero_budget():
    obj1 = LearningObjective("1", "cap_A", "reason", 10.0, 10.0, "art", "stop",
                             [], [], Assessment("a", "crit", 0.8, "test"))

    plan = sequence([obj1], {}, 0.0)

    assert plan.status == "DRAFT"
    assert len(plan.objectives) == 0

def test_deterministic_sequencing():
    evidence = [
        GapEvidence("1", EvidenceType.MISSING_NODE, "cap_A", "2023-01-01", {}, 5.0, 1),
        GapEvidence("2", EvidenceType.MISSING_NODE, "cap_B", "2023-01-01", {}, 5.0, 1)
    ]
    catalog = {
        "cap_A": {"capability_id": "cap_A", "base_cost": 10.0},
        "cap_B": {"capability_id": "cap_B", "base_cost": 10.0}
    }

    # Using fixed seed for deterministic output
    obj_list1 = build_objectives(infer_gaps(evidence), catalog, {}, seed=42)
    obj_list2 = build_objectives(infer_gaps(evidence), catalog, {}, seed=42)

    # Priority should match since they have same inputs, seed keeps generation deterministic if any random logic was used
    assert obj_list1[0].target_capability_id == obj_list2[0].target_capability_id

    plan1 = sequence(obj_list1, {}, 100.0)
    plan2 = sequence(obj_list2, {}, 100.0)

    assert [o.target_capability_id for o in plan1.objectives] == [o.target_capability_id for o in plan2.objectives]

def test_plan_revision():
    obj1 = LearningObjective("1", "cap_A", "reason", 10.0, 10.0, "art", "stop",
                             [], [], Assessment("a", "crit", 0.8, "test"))
    obj2 = LearningObjective("2", "cap_B", "reason", 10.0, 10.0, "art", "stop",
                             [], [], Assessment("a", "crit", 0.8, "test"))

    plan = CurriculumPlan("plan_1", [obj1, obj2], 20.0, 100.0, "1.0", "APPROVED")

    # Cap A passed, Cap B failed
    results = {"1": True, "2": False}

    revised_plan = revise(plan, results)

    assert len(revised_plan.objectives) == 1
    assert revised_plan.objectives[0].id == "2"
    assert revised_plan.total_cost == 10.0
    assert revised_plan.status == "REVISED"

def test_explain_plan():
    obj1 = LearningObjective("1", "cap_A", "reason", 10.0, 10.0, "art", "stop",
                             [], [], Assessment("a", "crit", 0.8, "test"))
    plan = CurriculumPlan("plan_1", [obj1], 10.0, 100.0, "1.0", "APPROVED")

    plan_store = {"plan_1": plan}

    explanation = explain("plan_1", plan_store)

    assert explanation["plan_id"] == "plan_1"
    assert explanation["status"] == "APPROVED"
    assert len(explanation["reasoning"]) == 1

def test_foundational_gap():
    evidence = [
        GapEvidence("1", EvidenceType.MISSING_NODE, "cap_core", "2023-01-01", {}, 100.0, 1)
    ]
    catalog = {
        "cap_core": {"capability_id": "cap_core", "base_cost": 50.0}
    }

    objectives = build_objectives(infer_gaps(evidence), catalog, {"impact_weight": 2.0})

    assert len(objectives) == 1
    assert objectives[0].priority_score > 100.0
    assert objectives[0].study_units[0].type == "KNOWLEDGE_ACQUISITION"

def test_impossible_objectives():
    # If a prerequisite is not available in the graph, it should not be scheduled.
    obj1 = LearningObjective("1", "cap_A", "reason", 10.0, 10.0, "art", "stop",
                             [Prerequisite("cap_Z", True)], [], Assessment("a", "crit", 0.8, "test"))

    plan = sequence([obj1], {}, 100.0)

    assert len(plan.objectives) == 0

def test_conflicting_priorities():
    evidence = [
        GapEvidence("1", EvidenceType.TASK_FAILURE, "cap_A", "2023-01-01", {}, 10.0, 5), # High impact, high recurrence
        GapEvidence("2", EvidenceType.MISSING_NODE, "cap_B", "2023-01-01", {}, 2.0, 1)   # Low impact, low recurrence
    ]
    catalog = {
        "cap_A": {"capability_id": "cap_A", "base_cost": 10.0},
        "cap_B": {"capability_id": "cap_B", "base_cost": 10.0}
    }

    objectives = build_objectives(infer_gaps(evidence), catalog, {"impact_weight": 1.0, "recurrence_weight": 1.0})

    assert objectives[0].target_capability_id == "cap_A"
    assert objectives[1].target_capability_id == "cap_B"
    assert objectives[0].priority_score > objectives[1].priority_score

def test_stale_gap_evidence():
    # Only the most recent impact/context should be considered when deduplicating,
    # though recurrence should be summed.
    evidence = [
        GapEvidence("1", EvidenceType.TASK_FAILURE, "cap_A", "2023-01-01T10:00:00", {"info": "old"}, 2.0, 1),
        GapEvidence("2", EvidenceType.TASK_FAILURE, "cap_A", "2023-01-02T10:00:00", {"info": "new"}, 10.0, 1),
    ]

    gaps = infer_gaps(evidence)

    assert len(gaps) == 1
    assert gaps[0].recurrence_count == 2
    assert gaps[0].impact_score == 10.0 # Using max here based on current implementation
    assert gaps[0].timestamp == "2023-01-02T10:00:00"
