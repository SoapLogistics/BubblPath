from typing import List, Dict, Optional, Set
from .models import GapEvidence, LearningObjective, CurriculumPlan, Prerequisite, StudyUnit, Assessment
import random
import uuid

# Registry metadata for engine compliance
route_key = "oswald_curriculum_planner"
readiness_key = "oswald_curriculum_planner_ready"
internal_parent = "oswald_curriculum"
retired_reason = None

class CurriculumPlanner:
    def __init__(self, catalog: Optional[Dict] = None, policy: Optional[Dict] = None):
        self.catalog = catalog or {}
        self.policy = policy or {}

    def infer_gaps(self, evidence: List[GapEvidence]) -> List[Dict]:
        """Aggregate and deduplicate gaps from raw evidence."""
        gap_clusters = {}
        for ev in evidence:
            # Simple grouping by related concept (or fallback to source)
            # A real implementation might use embeddings here, but we keep it deterministic
            key = ev.description.lower().strip()
            if key not in gap_clusters:
                gap_clusters[key] = []
            gap_clusters[key].append(ev)

        gaps = []
        for key, cluster in gap_clusters.items():
            avg_importance = sum(e.importance for e in cluster) / len(cluster)
            avg_confidence = sum(e.confidence for e in cluster) / len(cluster)

            # More important + less confident = higher gap priority
            gap_priority = avg_importance * (1.0 - avg_confidence)

            gaps.append({
                "description": key,
                "priority": gap_priority,
                "evidence_count": len(cluster),
                "related_nodes": list({node for ev in cluster for node in ev.related_nodes})
            })

        # Sort by priority
        gaps.sort(key=lambda x: x["priority"], reverse=True)
        return gaps

    def build_objectives(self, gaps: List[Dict], seed: Optional[int] = None) -> List[LearningObjective]:
        """Convert gaps into actionable learning objectives."""
        if seed is not None:
            random.seed(seed)

        objectives = []
        for i, gap in enumerate(gaps):
            # Deterministic ID if seeded, else random
            obj_id = f"obj_{uuid.uuid4().hex[:8]}" if seed is None else f"obj_{seed}_{i}"

            # Simple heuristic: map gap priority to objective priority score
            score = gap["priority"] * 10.0

            # Create a default assessment based on gap
            assessment = Assessment(
                method="quiz",
                passing_score=0.8,
                description=f"Verify mastery of: {gap['description']}"
            )

            # Create a default study unit
            unit = StudyUnit(
                title=f"Study: {gap['description']}",
                description=f"Review materials for {gap['description']}",
                estimated_cost=1.0, # base cost
                unit_type="knowledge",
                expected_artifact="Summary notes"
            )

            obj = LearningObjective(
                id=obj_id,
                title=f"Master {gap['description']}",
                description=f"Address gap identified from {gap['evidence_count']} sources.",
                priority_score=score,
                assessment=assessment,
                study_units=[unit],
                stop_condition=f"Score > 80% on assessment for {gap['description']}"
            )
            objectives.append(obj)

        return objectives

    def _detect_cycles(self, objectives: List[LearningObjective]) -> List[List[str]]:
        """Detect circular dependencies in objectives."""
        graph = {obj.id: [p.objective_id for p in obj.prerequisites] for obj in objectives}

        visited = set()
        path = []
        cycles = []

        def dfs(node):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor)

            path.pop()

        for node in graph:
            dfs(node)

        return cycles

    def _topological_sort(self, objectives: List[LearningObjective]) -> List[LearningObjective]:
        """Sort objectives satisfying dependencies."""
        graph = {obj.id: [p.objective_id for p in obj.prerequisites] for obj in objectives}
        in_degree = {obj.id: 0 for obj in objectives}

        for u in graph:
            for v in graph[u]:
                if v in in_degree:
                    in_degree[v] += 1

        queue = [u for u in in_degree if in_degree[u] == 0]
        # Sort queue deterministically by priority (higher is better) then ID
        queue.sort(key=lambda x: (
            next((o.priority_score for o in objectives if o.id == x), 0),
            x
        ), reverse=True)

        result_ids = []
        while queue:
            # Re-sort to maintain priority order among available nodes
            queue.sort(key=lambda x: (
                next((o.priority_score for o in objectives if o.id == x), 0),
                x
            ), reverse=True)
            u = queue.pop(0)
            result_ids.append(u)

            for v in graph.get(u, []):
                if v in in_degree:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        queue.append(v)

        # Map IDs back to objects
        obj_map = {obj.id: obj for obj in objectives}
        return [obj_map[uid] for uid in result_ids]

    def sequence(self, objectives: List[LearningObjective], budget: float, seed: Optional[int] = None) -> CurriculumPlan:
        """Sequence objectives based on priority, dependencies, and budget."""
        cycles = self._detect_cycles(objectives)
        if cycles:
            raise ValueError(f"Circular dependencies detected: {cycles}")

        sorted_objs = self._topological_sort(objectives)

        selected = []
        current_cost = 0.0

        for obj in sorted_objs:
            obj_cost = sum(u.estimated_cost for u in obj.study_units)
            if current_cost + obj_cost <= budget:
                selected.append(obj)
                current_cost += obj_cost

        plan = CurriculumPlan(
            objectives=selected,
            budget=budget,
            consumed_budget=current_cost,
            seed=seed
        )
        return plan

    def revise(self, plan: CurriculumPlan, assessment_results: Dict[str, Dict]) -> CurriculumPlan:
        """Update plan based on assessment results."""
        new_objectives = []
        for obj in plan.objectives:
            result = assessment_results.get(obj.id)
            if result:
                score = result.get("score", 0.0)
                if score >= obj.assessment.passing_score:
                    obj.status = "completed"
                else:
                    obj.status = "failed"
                    # Maybe increase priority for next time
                    obj.priority_score *= 1.2
            new_objectives.append(obj)

        plan.objectives = new_objectives
        return plan

    def explain(self, plan: CurriculumPlan) -> Dict:
        """Provide an explanation for the generated plan."""
        explanation = {
            "plan_id": plan.id,
            "total_budget": plan.budget,
            "consumed_budget": plan.consumed_budget,
            "objective_count": len(plan.objectives),
            "objectives": []
        }

        for obj in plan.objectives:
            explanation["objectives"].append({
                "id": obj.id,
                "title": obj.title,
                "priority": obj.priority_score,
                "cost": sum(u.estimated_cost for u in obj.study_units),
                "prerequisites": [p.objective_id for p in obj.prerequisites],
                "status": obj.status
            })

        return explanation
