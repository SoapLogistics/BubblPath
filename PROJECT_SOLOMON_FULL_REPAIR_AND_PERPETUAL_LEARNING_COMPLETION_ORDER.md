# PROJECT SOLOMON — FULL REPAIR AND PERPETUAL-LEARNING COMPLETION ORDER

**Primary executor:** Jules / Antigravity
**Authority:** Mark Miller / Project Solomon
**Repository last reported:** `/app`
**Remote last reported:** `https://github.com/SoapLogistics/BubblPath`
**Branch last reported:** `jules-13384773238309533918-912b2a35`
**Commit last reported:** `4d4a01f739ea65d34e8ee2838c112785b50d1e7a`
**Environment last reported:** `SANDBOX_DEV`
**Current evidence-backed maturity:** Level 3/7
**Directive type:** Execute, repair, validate, integrate, deploy, and certify
**Completion target:** One coherent, governed, restart-safe, evidence-backed perpetual-learning system

---

## 0. READ THIS FIRST

This directive is not asking for another inventory, another rewritten audit, another status summary, or another ZIP containing mostly the same evidence.

The repeated Jules evidence packages have already established the current condition:
- 21 registered components.
- 12 present in some form.
- 9 missing.
- 25 tests passing.
- Zero warnings in the latest verified baseline.
- Dirty working tree.
- Multiple fragmented state stores.
- `memory_atoms.db` repeatedly accumulating duplicate empty lesson rows.
- `memory_atoms.db` later omitted from evidence without proof of repair.
- Governance history shrinking between archives instead of remaining append-only.
- No real end-to-end learning trace.
- No resident framework.
- No restart or reboot proof.
- No canonical database migration.
- No backup/restore proof.
- No SS2 → SS3 → SS1 promotion proof.
- No live God Eye backend.
- No production service manager.
- No evidence-backed perpetual-learning cycle.

The work now is implementation.

> Do not produce another inventory until the code, tests, runtime, and evidence have materially changed.
> Do not hide defective files from the evidence package.
> Do not call a static HTML page integrated.
> Do not call a script scheduled unless a real scheduler runs it.
> Do not call a unit-test mock a live closed loop.
> Do not call a status-only binary file governance.
> Do not call repeated empty database rows learning.
> Do not call a sandbox production.
> Do not call a process perpetual until it survives restart and continues.

---

## 1. FINAL SYSTEM TARGET

Project Solomon must become a single coordinated system that can:
1. Observe tasks, failures, corrections, outcomes, and opportunities.
2. Convert useful observations into structured learning candidates.
3. Reject empty, duplicate, unsupported, unsafe, or low-value candidates.
4. Validate useful candidates.
5. Route risky candidates through governance.
6. Store approved knowledge in one canonical database.
7. Index activated knowledge.
8. Retrieve relevant knowledge before planning.
9. Apply relevant knowledge during execution.
10. Record whether the knowledge helped, hurt, or was irrelevant.
11. Update confidence and utility from the outcome.
12. Select the next highest-value learning target.
13. Execute bounded learning work in SS2.
14. Validate independently in SS3.
15. Promote safely into SS1 only after approval.
16. Checkpoint every autonomous cycle.
17. Survive process restart and machine reboot.
18. Preserve complete governance and event history.
19. Back up and restore state.
20. Expose truthful health and learning metrics.
21. Continue operating without a fresh human prompt for every cycle.
22. Never spend money, place bets, make irreversible external changes, or cross Mark’s approval boundary without explicit authorization.

The complete loop is:
```text
OBSERVE
  -> CLASSIFY
  -> DRAFT CANDIDATE
  -> DEDUPLICATE
  -> VALIDATE
  -> GOVERN
  -> ACTIVATE
  -> INDEX
  -> RETRIEVE BEFORE PLANNING
  -> APPLY
  -> MEASURE OUTCOME
  -> UPDATE MEMORY
  -> SELECT NEXT TARGET
  -> EXECUTE SAFELY
  -> CHECKPOINT
  -> REPEAT
```
Every arrow must be proven.

---

## 2. NON-NEGOTIABLE RULES

### 2.1 Stop evidence-only work
Do not spend another cycle merely:
- renaming inventory files,
- removing embarrassing artifacts,
- rewriting maturity labels,
- reusing unchanged test output,
- repackaging old reports,
- or hiding state files.

*Every new evidence package must contain at least one meaningful implementation change and new test evidence.*

### 2.2 Preserve evidence transparency
If a file is modified, include it or include:
- exact path,
- size,
- SHA-256 before,
- SHA-256 after,
- schema or format,
- inspection output,
- reason for modification.

*Never omit a defective database merely to make the ZIP look cleaner.*

### 2.3 One canonical authority per concern
There must be exactly one canonical:
- production database,
- database connection factory,
- migration owner,
- memory lifecycle,
- capability registry,
- lifecycle manager,
- scheduler/resident framework,
- governance record,
- configuration system,
- deployment promotion path.

*Adapters are allowed. Competing authorities are not.*

### 2.4 Tests must not contaminate production or repository state
A full test run must leave all repository-root and production state files byte-for-byte unchanged. Tests must use temporary isolated state.

### 2.5 Evidence must be tied to a clean commit
Final evidence must include:
- `git status --porcelain` (must be empty for certification)
- `git rev-parse HEAD`
- `git diff --stat`
- exact test command
- dependency snapshot
- environment identity
- artifact manifest

### 2.6 No silent self-modification
Solomon may propose and test modifications in SS2. Solomon may not silently promote changes into SS1. Protected files, dependencies, privileges, network exposure, secrets, financial actions, and irreversible actions require governance.

### 2.7 Optimize only after correctness
Do not build exotic O(1), zero-copy, memory-mapped, quantized, compressed, or distributed systems merely to satisfy prior language.
1. Correctness.
2. Measurement.
3. Baseline.
4. Bottleneck identification.
5. Optimization.
6. Quality comparison.
7. Rollback.

---

## 3. CURRENT DEFECT REGISTER

### P0 — State integrity and truth
- Dirty working tree.
- Stale or inconsistent runtime identity.
- Tests mutating `memory_atoms.db`.
- Duplicate empty lesson rows accumulating across runs.
- `memory_atoms.db` later omitted from evidence without proof of repair.
- Multiple competing stores: `memory_atoms.db`, `solomon_soss.db`, `solomon_brain_map.bin`, `governance_log.bin`, `fact_memory.log`.
- No proven canonical database.
- No database migration proof.
- No clean release commit.
- No root-state immutability test.

### P0 — Governance integrity
- Governance file records only repeated statuses.
- Records contain `unknown`.
- Prior governance cycles disappeared between archives.
- History is not durable.
- History is not append-only.
- Requests cannot be reconstructed.
- Artifact hashes are absent.
- Test evidence is absent.
- Reviewer and reason are absent.
- Rollback and promotion evidence are absent.
- Tamper detection is absent.

### P0 — Learning loop
- Empty lessons are accepted.
- Duplicate candidates are accepted.
- Candidate lifecycle is not proven.
- Validation is not proven end to end.
- Activation is not proven.
- Retrieval before planning is not proven.
- Application tracking is not proven.
- Outcome-linked utility update is not proven.
- Next-target selection is not proven.
- Autonomous repetition is not proven.

### P1 — Missing core components
- `core/swarm/resident_framework.py`
- `services/solomon_guardian_resident.py`
- `services/solomon_jules_resident.py`
- `services/solomon_validation_framework.py` or a canonical equivalent
- `backend/services/god_eye_bridge.py`
- `backend/services/resident_dashboard.py`
- `backend/services/health_dashboard.py`
- `core/solomon_quantized_efficiency.py`
- `core/solomon_hyper_registry.py`

*The last two must not be implemented prematurely. First decide whether existing components can fulfill their roles.*

### P1 — Security
- Dynamic imports from potentially compromised paths.
- Path traversal.
- Symlink escape.
- Unsigned execution requests.
- Unauthorized writeback.
- Weak actor provenance.
- Debug traceback exposure.
- Unpinned frontend dependencies.
- No proven environment-promotion boundary.
- Negative security test suite.

### P1 — Deployment and continuity
- No service manager.
- No resident lifecycle.
- No durable checkpoint.
- No duplicate-work lease.
- No process restart proof.
- No host reboot proof.
- No automated backup.
- No restore drill.
- No SS3 independent validation.
- No SS1 promotion record.

---

## 4. EXECUTION ORDER

*Execute these phases in order. Do not skip ahead.*

### PHASE 0 — CREATE A REAL CHECKPOINT
1. Locate the real repository.
2. Confirm branch and remote.
3. Save the current dirty diff.
4. Inspect every modified state file. Do not delete defective state.
5. Back up: databases, binary stores, logs, configuration, current evidence.
6. Create a repair branch.
7. Commit the current truthful baseline.
8. Regenerate runtime identity.

### PHASE 1 — FIX TEST ISOLATION FIRST
- All tests must use: `tmp_path`, temporary SQLite databases, temporary binary files, temporary logs, temporary checkpoint directories, isolated environment variables.
- No test may write: `./memory_atoms.db`, `./solomon_soss.db`, `./solomon_brain_map.bin`, `./governance_log.bin`, `./fact_memory.log`.
- Centralize state paths under one configuration object (`SolomonPaths`). Production paths come from validated configuration. Tests override the entire object.
- Add root-state immutability test: hash every root/production state file before and after the full suite. Fail if any hash differs.
- Add a CI repository scan: fail when test code or application code introduces unauthorized direct references to production-root state paths.

### PHASE 2 — REPAIR MEMORY WRITE QUALITY
- Define a real learning candidate schema.
- Reject empty content: content, title, provenance must be present.
- Add idempotency: use content hash, event ID, unique constraints.
- Migrate or quarantine existing duplicates.
- Add meaningful writeback answering what happened, why, and next actions.

### PHASE 3 — SELECT ONE CANONICAL DATABASE
- Inspect all candidate stores.
- Relational production database should be `solomon_soss.db`.
- Create one connection factory with WAL mode, busy timeout, foreign keys, and transactions enabled.
- Migrate active writers (scan, writeback, Futures engine, dashboards, cards).
- Define non-database artifacts (mmap acts only as cache).

### PHASE 4 — BUILD THE REAL MEMORY LIFECYCLE
- Handle candidates through state transitions (DRAFT -> VALIDATING -> REJECTED | APPROVED -> ACTIVE -> SUPERSEDED | QUARANTINED | ARCHIVED).
- Track confidence, utility, tag links, supersessions, and contradictions.

### PHASE 5 — PROVE RETRIEVAL BEFORE PLANNING
- Relevant memory must influence plans before execution begins. Persist query traces.

### PHASE 6 — PROVE OUTCOME-LINKED LEARNING
- Solomon must learn whether reused knowledge helped. Update confidence and utility.

### PHASE 7 — BUILD THE FIRST REAL CLOSED-LOOP TEST
- Create: `tests/integration/test_real_perpetual_learning_cycle.py`. Prove entire loop end-to-end.

### PHASE 8 — REPLACE GOVERNANCE WITH DURABLE DECISIONS
- Ensure governance records are append-only structured packets with sequences, hashes, test logs, reasons, and rollback plans.

### PHASE 9 — BUILD ONE CANONICAL RESIDENT FRAMEWORK
- Consolidate continuous background operations with checkpointing and leases.

### PHASE 10 — IMPLEMENT GUARDIAN AND JULES RESIDENTS
- Develop the guardian daemon and Jules convergence/repair daemon.

### PHASE 11 — CREATE A VALIDATION FRAMEWORK
- Implement type-appropriate validation proofs for every change.

### PHASE 12 — HARDEN GABRIEL CAPABILITY ACQUISITION
- Enforce path-bounds, dynamic import allowlists, and signature validations on dynamic loading.

### PHASE 13 — SECURE THE API AND WRITEBACK SURFACES
- Add authentication, authorization, error sanitization, and signature checks.

### PHASE 14 — COMPLETE FUTURES / LOKI OUTCOME LEARNING
- Establish Gate A/B outcomes, predictions snapshots, calibration scoring, and rule updates.

### PHASE 15 — BUILD LIVE HEALTH AND RESIDENT STATUS
- Expose real system metrics on the telemetry dashboards.

### PHASE 16 — CONNECT GOD EYE TO REAL MEMORY
- Feed the Three.js 3D force graph from live canonical memory node data.

### PHASE 17 — IMPLEMENT DEPLOYMENT ROLES
- Establish explicit SS2 development, SS3 independent review, and governed SS1 production rules.

### PHASE 18 — SERVICE MANAGER, RESTART, AND REBOOT
- Run as systemd/supervised containers surviving restarts and reboots.

### PHASE 19 — BACKUP AND RESTORE
- Automate state backups and verify restore drills.

### PHASE 20 — MEASURED QUANTIZED EFFICIENCY
- Quantize/optimize bottleneck nodes with quality and budget enforcement.

### PHASE 21 — SOAK TEST
- Operate repeatedly and safely over multi-cycle runs under failure injections.

---

## 5. REQUIRED FINAL TEST SUITE

The final suite must include at minimum:
- **State and database:** test isolation, duplicate prevention, canonical storage only, migrations, and concurrency.
- **Memory lifecycle:** candidate workflows, retrieval-before-planning, outcomes-linked updates.
- **Closed loop:** `test_real_perpetual_learning_cycle`.
- **Governance:** append-only hash chains, packet durability.
- **Residents:** leases, checkpoint resumes, restart/reboot.
- **Security:** path limits, import allowlists, unauthorized endpoint rejections.
- **Futures:** Gate A/B validation, outcome reconciliation, odds provenance.
- **Interfaces:** health status, live God Eye memory mapping.

---

## 6. REQUIRED EVIDENCE PACKAGE

Store inside: `SOLOMON_FULL_REPAIR_CERTIFICATION/` with complete MANIFEST hashes.

---

## 7. CERTIFICATION GATES

Solomon is certified only when all 14 Gates (Clean identity, Test isolation, Canonical storage, Memory quality, Lifecycle, Retrieval, Outcome, Closed loop, Governance, Residents, Security, Deployment, Recovery, Soak) pass successfully on a clean commit.

---

## 8. STOP CONDITIONS

*Stop and escalate on destructive migrations lacking backup, uncertain production paths, or potential bet/financial triggers.*

---

## 9. PROGRESS REPORTING FORMAT

Report metrics strictly using Section 9's format after every major phase.
