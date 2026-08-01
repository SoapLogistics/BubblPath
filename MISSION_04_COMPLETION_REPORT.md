# MISSION 04 — Self Curriculum Generator Completion Report

## Architecture Decisions
- **Modularity:** Isolated the curriculum models and logic into `backend/services/oswald/curriculum_models.py` and `backend/services/oswald/curriculum_generator.py` respectively, aligning with existing Oswald components.
- **Data Models:** Utilized Python `dataclasses` with strict typing and validation logic (e.g. `validate()` on `GapEvidence` and `CurriculumPlan`) for standard serialization (`to_dict`/`from_dict`).
- **Cycle Detection:** DFS-based topological cycle detection implemented directly in the planner, failing closed (status FAILED) and providing a `repair_proposal` to the orchestrator.
- **Deterministic Sequencing:** Prioritized greedy list scheduling against strict budgets, sorting by deterministic multi-factor priority scores (impact, recurrence, risk, centrality, effort). Supports a random seed for testing or stochastic exploration if desired.
- **Fail-Safe Integrity:** Invalid models raise exceptions upon creation (`ValueError`). Missing metadata safely defaults without halting the curriculum engine.

## Files Modified/Added
- `backend/services/oswald/__init__.py` (Added)
- `backend/services/oswald/curriculum_models.py` (Added)
- `backend/services/oswald/curriculum_generator.py` (Added)
- `tests/test_oswald_curriculum.py` (Added)

## Exact Public Interfaces
`backend/services/oswald/curriculum_generator.py`:
- `infer_gaps(evidence_list: List[GapEvidence]) -> List[GapEvidence]`
- `build_objectives(gaps: List[GapEvidence], catalog: Dict[str, Any], policy: Dict[str, Any], seed: Optional[int] = None) -> List[LearningObjective]`
- `sequence(objectives: List[LearningObjective], graph: Dict[str, List[str]], budget: float) -> CurriculumPlan`
- `revise(plan: CurriculumPlan, assessment_results: Dict[str, bool]) -> CurriculumPlan`
- `explain(plan_id: str, plan_store: Dict[str, CurriculumPlan]) -> Dict[str, Any]`

## Storage/Schema Changes
- Schemas strictly localized to Python data structures. Storage integration deferred to Claude per mission constraints. Models support explicit `to_dict()` for direct serialization into document DBs or SQL text columns via JSON.

## Test Results and Commands
Run all unit tests locally with:
```bash
PYTHONPATH=. python3 -m pytest tests/test_oswald_curriculum.py
```
- Total Tests: 10
- Coverage: Core sequencing, circular prerequisites, zero budget edge cases, priority weighting, gap aggregation logic.
- Results: 100% Pass.

## Known Limitations
- Resource Discovery is strictly mocked inside `build_objectives` mapping. External systems must populate the `catalog`.
- Priority weighting currently mocks "centrality, risk, effort". A true implementation needs these fields populated by the graph/KAC subsystem.
- Sequencing assumes simple capabilities without overlapping budget discounts.

## Recommended Wiring Order for Claude
1. Integrate `CurriculumPlan` serialization directly into Oswald's DB or Document storage.
2. Hook `infer_gaps` into Prometheus task failure events and Oswald low-confidence signals.
3. Call `build_objectives` and `sequence` inside a nightly/weekly cron or idle-worker loop.
4. Execute `revise` following laboratory or experiment outcomes.

## Rollback Instructions
If a rollback is required, simply remove the added Oswald curriculum files:
```bash
rm backend/services/oswald/curriculum_models.py
rm backend/services/oswald/curriculum_generator.py
rm tests/test_oswald_curriculum.py
```
Since this mission involved no live routing or daemon wiring, there is zero risk to live services.
