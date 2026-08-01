import uuid
import datetime
import random
from typing import List, Dict, Any, Optional, Set, Tuple

from backend.services.oswald.curriculum_models import (
    GapEvidence, EvidenceType, LearningObjective, CurriculumPlan,
    Prerequisite, Assessment, StudyUnit
)

def infer_gaps(evidence_list: List[GapEvidence]) -> List[GapEvidence]:
    """
    Aggregates gap evidence. Deduplicates failures, resolves contradictions,
    and groups missing nodes.
    """
    if not evidence_list:
        return []

    # Validation
    for e in evidence_list:
        e.validate()

    # Deduplication and aggregation logic based on source_identifier + evidence_type
    aggregated_gaps = {}
    for evidence in evidence_list:
        # Define a unique key for deduplication
        key = (evidence.source_identifier, evidence.evidence_type)
        if key in aggregated_gaps:
            existing = aggregated_gaps[key]
            # If newer timestamp or just counting recurrence
            if evidence.timestamp > existing.timestamp:
                existing.timestamp = evidence.timestamp
                existing.context.update(evidence.context)
            # Increase recurrence count, cap impact score or average it
            existing.recurrence_count += evidence.recurrence_count
            existing.impact_score = max(existing.impact_score, evidence.impact_score)
        else:
            aggregated_gaps[key] = evidence

    return list(aggregated_gaps.values())


def _calculate_priority(gap: GapEvidence, catalog: Dict[str, Any], policy: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """Calculates a priority score based on impact, recurrence, centrality, risk, and effort."""
    impact_weight = policy.get("impact_weight", 1.0)
    recurrence_weight = policy.get("recurrence_weight", 0.5)

    # Simple score components
    impact_score = gap.impact_score * impact_weight
    recurrence_score = min(gap.recurrence_count * recurrence_weight, 5.0) # Cap recurrence contribution

    # Mocking centrality, risk, effort from catalog mapping
    centrality_score = 1.0
    risk_score = 1.0
    effort_score = 1.0

    components = {
        "impact": impact_score,
        "recurrence": recurrence_score,
        "centrality": centrality_score,
        "risk": risk_score,
        "effort": effort_score
    }

    total_score = impact_score + recurrence_score + centrality_score + risk_score - effort_score
    return max(0.0, total_score), components

def build_objectives(gaps: List[GapEvidence], catalog: Dict[str, Any], policy: Dict[str, Any], seed: Optional[int] = None) -> List[LearningObjective]:
    """
    Converts gaps into learning objectives based on a capability catalog and learning policy.
    """
    if seed is not None:
        random.seed(seed)

    objectives = []

    for gap in gaps:
        # Lookup the capability mapping from catalog, if missing create a generic one
        mapping = catalog.get(gap.source_identifier, {})

        target_capability_id = mapping.get("capability_id", f"cap_{gap.source_identifier}")

        priority_score, score_components = _calculate_priority(gap, catalog, policy)

        # Determine prerequisites from catalog
        raw_prereqs = mapping.get("prerequisites", [])
        prerequisites = [Prerequisite(p["capability_id"], p.get("is_hard_blocker", True)) for p in raw_prereqs]

        # Create standard study units based on evidence type
        study_units = []
        estimated_cost = mapping.get("base_cost", 10.0)

        if gap.evidence_type == EvidenceType.MISSING_NODE:
            study_units.append(StudyUnit(
                id=str(uuid.uuid4()),
                type="KNOWLEDGE_ACQUISITION",
                description=f"Learn foundational concepts for {target_capability_id}",
                resource_descriptors=["docs", "tutorials"],
                estimated_cost=estimated_cost * 0.5
            ))
        elif gap.evidence_type == EvidenceType.TASK_FAILURE:
            study_units.append(StudyUnit(
                id=str(uuid.uuid4()),
                type="IMPLEMENTATION_PRACTICE",
                description=f"Practice implementation for {target_capability_id}",
                resource_descriptors=["sandboxes", "exercises"],
                estimated_cost=estimated_cost * 0.8
            ))

        obj = LearningObjective(
            id=str(uuid.uuid4()),
            target_capability_id=target_capability_id,
            reason=f"Addressed gap from {gap.evidence_type.value} on {gap.source_identifier}",
            priority_score=priority_score,
            estimated_cost=estimated_cost,
            expected_artifact=mapping.get("expected_artifact", "completion_report.md"),
            stop_condition=mapping.get("stop_condition", "assessment_passed"),
            prerequisites=prerequisites,
            study_units=study_units,
            assessment=Assessment(
                id=str(uuid.uuid4()),
                criteria="Pass standard test suite",
                passing_threshold=0.8,
                type="VERIFICATION"
            ),
            score_components=score_components
        )
        objectives.append(obj)

    # Sort by priority score descending
    objectives.sort(key=lambda x: x.priority_score, reverse=True)
    return objectives


def _detect_cycles(objectives: List[LearningObjective], graph: Dict[str, List[str]]) -> Tuple[List[str], Optional[str]]:
    """Detects cycles in the prerequisite graph using DFS."""
    visited = set()
    rec_stack = set()
    cycles = []

    # Build local graph from objectives + provided graph
    local_graph = {obj.target_capability_id: [] for obj in objectives}
    for obj in objectives:
        for p in obj.prerequisites:
            if p.capability_id in local_graph:
                local_graph[obj.target_capability_id].append(p.capability_id)
            elif p.capability_id in graph:
                local_graph[obj.target_capability_id].extend(graph[p.capability_id])

    def dfs(node: str, path: List[str]):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in local_graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in rec_stack:
                # Cycle detected
                cycle_start = path.index(neighbor)
                cycles.append(" -> ".join(path[cycle_start:] + [neighbor]))
                return True

        rec_stack.remove(node)
        path.pop()
        return False

    for node in list(local_graph.keys()):
        if node not in visited:
            if dfs(node, []):
                pass # Cycle recorded

    repair_proposal = None
    if cycles:
        repair_proposal = "Cycle detected in prerequisites. Review the cycle path and remove circular hard blockers."

    return cycles, repair_proposal

def sequence(objectives: List[LearningObjective], graph: Dict[str, List[str]], budget: float) -> CurriculumPlan:
    """
    Sequences objectives respecting prerequisites and budget constraints.
    Detects cycles.
    """
    cycles, repair_proposal = _detect_cycles(objectives, graph)

    if cycles:
        return CurriculumPlan(
            id=str(uuid.uuid4()),
            objectives=[],
            total_cost=0.0,
            budget=budget,
            status="FAILED",
            cycles_detected=cycles,
            repair_proposal=repair_proposal
        )

    # Sequence based on topological sort + priority
    # Simplified approach: greedily pick objectives whose prereqs are met and fit budget
    sequenced = []
    total_cost = 0.0
    completed_caps = set() # Capabilities we assume completed in this plan

    # Assuming external graph nodes are already met for simplicity in this greedy approach,
    # unless they are in the objectives list AND not met.
    # We will be stricter: if a prerequisite is NOT in objective_caps and NOT in completed_caps
    # and NOT explicitly in `graph` as a known/satisfied node, it's considered unfulfilled.
    objective_caps = {obj.target_capability_id for obj in objectives}

    pending = objectives.copy()

    while pending:
        progress_made = False
        for obj in pending:
            # Check if hard prereqs are met
            prereqs_met = True
            for p in obj.prerequisites:
                if p.is_hard_blocker:
                    # If it's a capability we need to learn (in objectives) but haven't yet, block.
                    if p.capability_id in objective_caps and p.capability_id not in completed_caps:
                        prereqs_met = False
                        break
                    # If it's not in objectives, check if it's considered fulfilled.
                    # Since we don't have a full user capability state passed in, we assume
                    # nodes in `graph` are the known universe of fulfilled external prerequisites,
                    # OR we could just pass in `completed_caps` explicitly to `sequence`.
                    # For now, if it's not in objective_caps and not in graph, it's an impossible objective.
                    elif p.capability_id not in objective_caps and p.capability_id not in graph:
                        prereqs_met = False
                        break

            if prereqs_met:
                if total_cost + obj.estimated_cost <= budget:
                    sequenced.append(obj)
                    total_cost += obj.estimated_cost
                    completed_caps.add(obj.target_capability_id)
                    pending.remove(obj)
                    progress_made = True
                    break # Restart scan to maintain priority order with new completed caps
                else:
                    # Budget constraint hit for this item, try next
                    continue

        if not progress_made:
            break # No more objectives can be scheduled due to prereqs or budget

    return CurriculumPlan(
        id=str(uuid.uuid4()),
        objectives=sequenced,
        total_cost=total_cost,
        budget=budget,
        status="APPROVED" if sequenced else "DRAFT"
    )

def revise(plan: CurriculumPlan, assessment_results: Dict[str, bool]) -> CurriculumPlan:
    """
    Revises a plan based on assessment results. Removes completed objectives.
    """
    revised_objectives = []
    total_cost = 0.0

    for obj in plan.objectives:
        passed = assessment_results.get(obj.id, False)
        if not passed:
            revised_objectives.append(obj)
            total_cost += obj.estimated_cost

    # Assuming budget remains the same, just keeping the remaining budget valid
    return CurriculumPlan(
        id=plan.id,
        objectives=revised_objectives,
        total_cost=total_cost,
        budget=plan.budget,
        status="REVISED"
    )

def explain(plan_id: str, plan_store: Dict[str, CurriculumPlan]) -> Dict[str, Any]:
    """
    Explains the reasoning behind a curriculum plan.
    """
    plan = plan_store.get(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    explanation = {
        "plan_id": plan.id,
        "status": plan.status,
        "budget_utilization": f"{plan.total_cost}/{plan.budget}",
        "objectives_count": len(plan.objectives),
        "reasoning": []
    }

    for i, obj in enumerate(plan.objectives):
        explanation["reasoning"].append({
            "sequence_order": i + 1,
            "target": obj.target_capability_id,
            "reason": obj.reason,
            "priority_score": obj.priority_score,
            "cost": obj.estimated_cost
        })

    if plan.cycles_detected:
        explanation["cycles"] = plan.cycles_detected
        explanation["repair_proposal"] = plan.repair_proposal

    return explanation
