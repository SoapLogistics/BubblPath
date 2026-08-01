# MISSION 06 — Hypothesis and Experiment Laboratory Core Completion Report

## 1. Goal Addressed
Implemented the core components for a hypothesis-driven experimentation lab. This enables the Solomon OS to advance toward perpetual learning by structuring its knowledge validation loop: generating falsifiable hypotheses, designing constrained experiments, and using rigorous observation to update foundational beliefs.

## 2. Modified Files
- `core/solomon_knowledge_cards/storage/db.py`: Added Migration 3 to generate SQLite tables for tracking hypotheses, experiment designs, observations, evaluations, and belief updates.
- `requirements.txt`: Added `scipy`, `numpy`, and `pydantic` to ensure necessary stats and validation components install cleanly.

## 3. Added Files
- `core/laboratory/models.py`: Immutable, versioned Pydantic models for `Hypothesis`, `ExperimentDesign`, `Observation`, `EvaluationResult`, `BeliefUpdateRecord`, and `ReproducibilityBundle`.
- `core/laboratory/repository.py`: A DAO layer wrapping the canonical `DatabaseManager` to persist and retrieve lab entities safely via locked JSON storage logic.
- `core/laboratory/executor.py`: A `Protocol` enforcing the contract for pluggable experiment executors.
- `core/laboratory/fake_executor.py`: A deterministic `FakeExecutor` for seeded observation generation and robust local testing.
- `core/laboratory/service.py`: The `LaboratoryService` managing the end-to-end experiment pipeline, relying on `scipy.stats` for foundational hypothesis testing and returning transparent evaluation updates.
- `tests/test_laboratory.py`: A comprehensive suite covering experiment validations, simulated runtime failures, database serialization round-trips, and null/success metrics testing.

## 4. Public Interfaces
- **Repository Methods**: `store_hypothesis`, `get_hypothesis`, `store_experiment_design`, `get_experiment_design`, `store_observation`, `get_observations_for_experiment`, `store_evaluation_result`, `get_evaluation_result`, `store_belief_update`.
- **Service API**: `register_hypothesis`, `design_experiment`, `validate_design`, `execute_and_evaluate`, `evaluate_results`, `propose_belief_update`, `export_reproducibility_bundle`.
- **Protocols**: `ExperimentExecutor.execute(design) -> List[Observation]`

## 5. Storage / Schema Changes
`db.py` contains **Migration 3**.
Added tables: `lab_hypotheses`, `lab_experiment_designs`, `lab_observations`, `lab_evaluation_results`, `lab_belief_updates`.
All tables use text-based IDs and JSON column arrays to remain flexible while being tightly audited via metadata.

## 6. Test Commands
```bash
PYTHONPATH=. python3 -m pytest tests/test_laboratory.py
```

## 7. Known Limitations
- Evaluation uses relatively rudimentary `ttest_1samp` evaluation against `0.0`. Complex multidimensional variables or varying experimental paradigms will necessitate a richer evaluation policy mapping.
- Currently, execution processes locally block while awaiting executor return. True long-running experiments will require an asynchronous or event-driven execution wrapper.
- Pydantic validation handles explicit bounds, but "logic checking" constraints (like validating `variables` content structures directly against a test environment) remains out of scope for the current design phase.

## 8. Recommended Wiring Order
1. Build specific integration implementations of `ExperimentExecutor` connecting to external APIs (e.g., Code Evaluation via Sandbox).
2. Establish cron jobs or daemon processes to scan memory updates and prompt `LaboratoryService.register_hypothesis`.
3. Link belief update approvals directly with the Governance pipeline (Mission 05 / MD6) so evaluations only mutate canonical memory post-approval.

## 9. Rollback Instructions
To rollback Migration 3:
Delete the tables directly using sqlite3:
```sql
DROP TABLE lab_belief_updates;
DROP TABLE lab_evaluation_results;
DROP TABLE lab_observations;
DROP TABLE lab_experiment_designs;
DROP TABLE lab_hypotheses;
DELETE FROM schema_version WHERE version = 3;
```
Revert the relevant codebase edits in `db.py` and delete the `core/laboratory` module folder.
