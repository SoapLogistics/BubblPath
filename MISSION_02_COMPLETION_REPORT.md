# MISSION 02: Contradiction Detection and Resolution Core

## 1. Executive Summary

This report documents the completion of Mission 02, focusing on the creation of a purely algorithmic contradiction detection and resolution module. The module parses incoming claims, matches related facts, classifies conflicts appropriately, and computes resolution proposals without inherently mutating or acting upon memory data itself.

## 2. Changed Files

### Files Added:
- `core/contradiction_core/__init__.py`: Public exposure of the contradiction module interfaces.
- `core/contradiction_core/models.py`: Defines schemas: `Claim`, `ClaimScope`, `ContradictionCase`, `ContradictionEvidence`, `ResolutionProposal`, and `ResolutionPolicy`.
- `core/contradiction_core/repository.py`: A local SQLite-backed persistence layer for storing ContradictionCases, preventing duplicate insertions via deterministic fingerprinting.
- `core/contradiction_core/detector.py`: The algorithmic brain containing rules for `CLASSIFICATION_TYPES` (Temporal, Numerical, Direct, Scoped, Definitional, Source Quality, Apparent).
- `core/contradiction_core/runner.py`: A batch processing utility for local test runs and local generation of the simulation docket.
- `tests/test_contradiction_core.py`: Unit and integration testing across models, classifications, persistence, and runners.

### System Impacts:
- No existing production files were modified.
- No direct linkages were established to live processes or agents.
- Avoided the earlier incorrect file deletion issues affecting the `gabriel_engine` directory.

## 3. Architecture Decisions

- **Immutability of Evaluation:** Resolution actions are formulated as proposals rather than imperative actions. The system classifies, scores severity/uncertainty, and suggests "SUPERSEDE" or "RETAIN_BOTH_WITH_SCOPE" without enforcing them.
- **Deterministic Hashing:** Added a unified `fingerprint()` logic on Claims and Cases. This explicitly fulfills the requirement to "deterministically collapse duplicate cases", preventing the pipeline from clogging up on repetitive identical statements.
- **Pluggable Policy:** Handled tolerance parameters (`numerical_tolerance`, `temporal_strictness`, `source_quality_threshold`) as a dynamically passable `ResolutionPolicy` struct.
- **Fail-Closed on Corrupted Data:** Explicit parameter validation checking within standard class instantiations (`validate()`) and explicit ISO date verifications are designed to throw `ValidationError` exceptions upon bad input rather than passing faulty state through the detector.

## 4. Test Commands and Results

* **Command:** `PYTHONPATH=. python3 -m pytest tests/test_contradiction_core.py`
* **Coverage:** 9 Tests Passed (100% success on suite).
* **Included Types:**
    * Validation enforcement (`test_claim_validation`)
    * Fingerprint deterministic outputs (`test_claim_fingerprint`)
    * Scope disjoint tests (`test_temporal_disjoint`)
    * Classification categorizations (`test_classify_direct`, `test_classify_temporal`, `test_classify_numerical`)
    * Ranking and severity evaluation (`test_detect_and_rank`)
    * SQLite repository upserts (`test_repository_persistence`)
    * Local docket generation (`test_fixture_docket`)

## 5. Known Limitations

- **String Tolerance Limitations:** Text-based matches (`flat` vs `spherical`) rely purely on string equivalence right now (unless numerical or scoped). Semantic similarity using vector DB embeddings is expected in a future pipeline stage but is intentionally scoped out of this deterministic matching layer.
- **Advanced Unit Conversion:** The module extracts numerals, but does not currently auto-convert complex units (e.g., `km/s` to `mph`) before performing the numerical tolerance check unless the exact same text unit string is used.

## 6. Integration Contract (For Claude)

The public API is explicitly exposed via `core.contradiction_core`.

```python
from core.contradiction_core import (
    Claim, ContradictionEvidence, ResolutionPolicy,
    ContradictionRepository, detect, rank, propose_resolution
)

# 1. Initialize dependencies
repo = ContradictionRepository("db_path.sqlite")
policy = ResolutionPolicy(numerical_tolerance=0.05, source_quality_threshold=0.3)

# 2. Extract Claims and Evidence (from Mnemosyne or incoming pipelines)
records = [(claim_obj, evidence_obj), ...]

# 3. Detect and save
cases = detect(records, policy)
for case in cases:
    repo.store_case(case) # Deterministic collision checking built-in

# 4. Action proposals
ranked_cases = rank(cases)
proposals = ranked_cases[0].proposals
```

## 7. Rollback Instructions

To roll back this integration, remove the `core/contradiction_core/` and `tests/test_contradiction_core.py` files. No external database migrations or API endpoints were launched, making rollback completely isolated to file removal.
