# PROJECT SOLOMON — CURRENT EVIDENCE-BASED INVENTORY

**Inventory date:** July 27, 2026
**Inventory type:** Repository/evidence inventory, not a completion claim
**Source archive:** `jules_session_13384773238309533918 (1).zip`
**Source archive SHA-256:** `64f877db16d6805678059a43db4bc539b1160cc6a6d6d3de01272d50ba8c73b2`
**Reported repository:** `/app`
**Reported remote:** `https://github.com/SoapLogistics/BubblPath`
**Reported branch:** `jules-13384773238309533918-912b2a35`
**Reported commit:** `a138dfff0c09d23397dafa46eeac261aca74994d`
**Reported environment:** `SANDBOX_DEV`

---

## 1. Inventory Verdict

The latest Jules package establishes a useful repository snapshot and a passing core test baseline. It does not establish a completed perpetual-learning system or production deployment.

The supplied registry lists 21 components:
- **6 present** with at least some supplied test evidence
- **4 present** but incomplete or not proven in live runtime
- **2 present** only as static or unwired interface components
- **9 missing**

The most accurate current description is:
> Sandbox development prototype with a tested core, fragmented storage, incomplete governance, no proven resident autonomy, and no evidence-backed perpetual learning loop.

---

## 2. Repository and Runtime Identity

| Field | Current evidence |
| :--- | :--- |
| **Captured at** | 2026-07-27T07:53:03Z |
| **Host** | devbox |
| **Operating system** | Ubuntu 24.04.4 LTS |
| **Kernel** | Linux devbox 6.8.0 #1 SMP PREEMPT_DYNAMIC Fri Feb 20 20:38:43 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux |
| **Repository path** | /app |
| **Git remote** | https://github.com/SoapLogistics/BubblPath |
| **Branch** | jules-13384773238309533918-912b2a35 |
| **Commit** | a138dfff0c09d23397dafa46eeac261aca74994d |
| **Git status** | M SOLOMON_PERPETUAL_LEARNING_MASTER_AUDIT.md, M fact_memory.log, M governance_log.bin, M memory_atoms.db |
| **Python** | Python 3.12.13 |
| **Python environment** | /home/jules/.pyenv/shims/python |
| **Service manager** | none (docker/sandbox container) |
| **Deployment environment** | SANDBOX_DEV |
| **Operator** | jules |

### Identity limitations
- The working tree was dirty when the evidence was captured.
- The archive does not contain the complete source repository, so file existence and test results cannot be independently reproduced from the upload alone.
- The environment is a sandbox/container, not proven SS1 production.
- No service manager is active in the reported environment.

---

## 3. Component Inventory

### Status meanings:
- **PRESENT — TESTED**: Code exists and at least one supplied test exercises the subsystem or a central path.
- **PRESENT — PARTIAL**: Code exists, but direct tests, runtime wiring, safety, or lifecycle proof is incomplete.
- **STATIC/UNWIRED**: Interface file exists without a proven live backend or route.
- **MISSING**: The exact claimed implementation is absent.

| # | Component | Path | Evidence-based status | What is proven | Main missing work |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | High-Performance Quantized Memory Engine | `solomon_quantized_memory.py` | PRESENT — PARTIAL | File exists and `app.py` reportedly calls it; no direct test file is present. | Add direct serialization, corruption, path-boundary, recall-quality, and restart tests. |
| 2 | Mnemosyne Knowledge Cards Module | `core/solomon_knowledge_cards/` | PRESENT — UNPROVEN RUNTIME | Package exists and points to `solomon_soss.db`; the referenced core test suite is absent. | Prove runtime wiring, lifecycle transitions, retrieval, provenance, deduplication, and migrations. |
| 3 | SQLite Database Manager | `core/solomon_knowledge_cards/storage/db.py` | PRESENT — PARTIAL | `DatabaseManager` exists with WAL/busy-timeout claims; it has no direct tests. | Make it the single connection authority and add migration, concurrency, backup, restore, and integrity tests. |
| 4 | Solomon Loki Futures Engine | `services/solomon_futures_engine.py` | PRESENT — TESTED CORE | File exists; threshold logic has five passing tests. | Add outcome reconciliation, calibration, idempotency, provenance, and financial-action boundary tests. |
| 5 | Daily Scan Orchestration Script | `scripts/run_daily_scan.py` | PRESENT — TESTED, NOT SCHEDULED | Script exists and one test passes; no runtime scheduler call site is documented. | Wire it to a governed scheduler/resident and prove idempotent repeated runs. |
| 6 | Governance Approval Packet | `services/solomon_governance_approval_packet.py` | PRESENT — TESTED PROTOTYPE | File exists and two tests pass; the binary evidence is status-only and non-reconstructable. | Replace or wrap binary status slots with complete append-only approval packets and tamper evidence. |
| 7 | Quantized Engine Budget & Efficiency Guard | `core/solomon_quantized_efficiency.py` | MISSING | The named file is absent; only a basic context budgeter is mentioned. | Decide whether to implement a measured budget layer or remove the unsupported claim. |
| 8 | Gabriel Capability Assimilation Engine | `gabriel_engine/` | PRESENT — TESTED LAB | Package exists; fourteen Gabriel-related tests pass. | Harden dynamic loading, path controls, manifests, permissions, provenance, sandboxing, and promotion gates. |
| 9 | Resident Daemon Framework | `core/swarm/resident_framework.py` | MISSING | No resident framework file exists. | Implement one lifecycle/checkpoint/lease framework only after the direct learning loop works. |
| 10 | Guardian Resident Daemon | `services/solomon_guardian_resident.py` | MISSING | No Guardian resident file exists. | Implement bounded health, recovery, resource, and escalation duties on the canonical resident framework. |
| 11 | Jules Resident Daemon | `services/solomon_jules_resident.py` | MISSING | No Jules resident file exists. | Implement repository convergence and validation work on the canonical resident framework. |
| 12 | MD8 Testing & Verification Framework | `services/solomon_validation_framework.py` | MISSING | The claimed MD8 validation framework does not exist. | Use a correct, testable validation framework first; optimize only after measurement. |
| 13 | God Eye Bridge API | `backend/services/god_eye_bridge.py` | MISSING | No backend graph bridge exists. | Implement the canonical memory graph endpoint and prove data lineage. |
| 14 | God Eye Real-Time Dashboard UI | `templates/god_eye.html` | PRESENT — STATIC/UNWIRED | HTML exists but calls a backend route the registry says does not exist. | Do not call it live until the bridge, route, tests, stale-state handling, and provenance view exist. |
| 15 | Futures Dashboard Backend API | `backend/services/futures_dashboard_backend.py` | PRESENT — PARTIAL | Backend exists and `app.py` reportedly calls it; it writes to legacy `memory_atoms.db`. | Move it to canonical storage, add auth/signature checks, route tests, and outcome writeback. |
| 16 | Futures Prediction Dashboard UI | `templates/futures_dashboard.html` | PRESENT — STATIC/UNPROVEN | HTML exists; no tests or runtime call site are recorded. | Add route/render tests, CSP, pinned dependencies, error states, and live backend proof. |
| 17 | Resident Daemon Dashboard API | `backend/services/resident_dashboard.py` | MISSING | No resident status API exists. | Build only after residents and checkpoints are real. |
| 18 | Global Health & Telemetry Dashboard | `backend/services/health_dashboard.py` | MISSING | No global health service exists. | Expose real service, database, queue, checkpoint, backup, and failure status after lifecycle convergence. |
| 19 | Hyper Registry Manager | `core/solomon_hyper_registry.py` | MISSING | The claimed hyper registry file does not exist. | Choose one simple canonical registry; add dependency and duplicate-registration tests before optimizing. |
| 20 | Learning Writeback Service | `services/solomon_learning_writeback.py` | PRESENT — TESTED PROTOTYPE | File exists and one test passes. | Require actor identity, provenance, authorization, validation result, idempotency, and outcome linkage. |
| 21 | Solomon Core Gateway Application | `app.py` | PRESENT — TESTED SANDBOX GATEWAY | `app.py` exists; Gabriel endpoint tests pass; no production service manager is present. | Create a single lifecycle owner, production config, authentication, safe errors, health probes, startup/restart proof, and service management. |

---

## 4. Present Components With Supplied Test Evidence

### Solomon Loki Futures Engine
- **Path:** `services/solomon_futures_engine.py`
- **Status:** PRESENT — TESTED CORE
- **Evidence:** File exists; threshold logic has five passing tests.
- **Tests named by registry:** `tests/futures/test_threshold_logic.py`
- **Runtime call sites:** `backend/services/futures_dashboard_backend.py`
- **Storage:** `solomon_soss.db`
- **Known concern:** Direct file-based checkpoint locks can suffer from race conditions.
- **Required next condition:** Add outcome reconciliation, calibration, idempotency, provenance, and financial-action boundary tests.

### Daily Scan Orchestration Script
- **Path:** `scripts/run_daily_scan.py`
- **Status:** PRESENT — TESTED, NOT SCHEDULED
- **Evidence:** Script exists and one test passes; no runtime scheduler call site is documented.
- **Tests named by registry:** `tests/test_run_daily_scan.py`
- **Runtime call sites:** None (intended for CLI scheduler execution)
- **Storage:** `memory_atoms.db`
- **Known concern:** Uses direct evaluation/formatting of subprocess execution context without sandboxing.
- **Required next condition:** Wire it to a governed scheduler/resident and prove idempotent repeated runs.

### Governance Approval Packet
- **Path:** `services/solomon_governance_approval_packet.py`
- **Status:** PRESENT — TESTED PROTOTYPE
- **Evidence:** File exists and two tests pass; the binary evidence is status-only and non-reconstructable.
- **Tests named by registry:** `tests/test_governance_approval.py`
- **Runtime call sites:** `app.py`
- **Storage:** None
- **Known concern:** `governance_log.bin` write boundaries rely on simple raw struct packs which could overwrite prior events if offset pointers drift.
- **Required next condition:** Replace or wrap binary status slots with complete append-only approval packets and tamper evidence.

### Gabriel Capability Assimilation Engine
- **Path:** `gabriel_engine/`
- **Status:** PRESENT — TESTED LAB
- **Evidence:** Package exists; fourteen Gabriel-related tests pass.
- **Tests named by registry:** `tests/test_gabriel.py`, `tests/test_gabriel_evolution.py`
- **Runtime call sites:** `app.py`
- **Storage:** `memory_atoms.db` (used inside capabilities like `renewable_worker_lease.py`)
- **Known concern:** Dynamic imports of unapproved Python modules via `dynamic_loader.py` are vulnerable to directory traversal and remote code execution if capability directories are compromised.
- **Required next condition:** Harden dynamic loading, path controls, manifests, permissions, provenance, sandboxing, and promotion gates.

### Learning Writeback Service
- **Path:** `services/solomon_learning_writeback.py`
- **Status:** PRESENT — TESTED PROTOTYPE
- **Evidence:** File exists and one test passes.
- **Tests named by registry:** `tests/test_learning_writeback.py`
- **Runtime call sites:** `app.py`
- **Storage:** None (interacts via local flask route)
- **Known concern:** Allows memory updates without strong signature validations or actor provenance checks.
- **Required next condition:** Require actor identity, provenance, authorization, validation result, idempotency, and outcome linkage.

### Solomon Core Gateway Application
- **Path:** `app.py`
- **Status:** PRESENT — TESTED SANDBOX GATEWAY
- **Evidence:** `app.py` exists; Gabriel endpoint tests pass; no production service manager is present.
- **Tests named by registry:** `tests/test_gabriel.py`
- **Runtime call sites:** Standalone runtime
- **Storage:** `memory_atoms.db` (implicitly loaded via capability configurations)
- **Known concern:** Global Flask error handler outputs tracebacks if in debug mode, potentially exposing sensitive database structure information.
- **Required next condition:** Create a single lifecycle owner, production config, authentication, safe errors, health probes, startup/restart proof, and service management.

---

## 5. Present but Incomplete Components

### High-Performance Quantized Memory Engine
- **Path:** `solomon_quantized_memory.py`
- **Status:** PRESENT — PARTIAL
- **Evidence:** File exists and `app.py` reportedly calls it; no direct test file is present.
- **Claimed purpose:** Provides a 1.58-bit ternary graph embedding layer, sparse matrix-vector multiplication spreading activation recall, Hebbian learning, and Ebbinghaus memory fading consolidation.
- **Runtime call sites:** `app.py`
- **Storage:** None (directly serializes to local binary file `solomon_brain_map.bin`)
- **Known concern:** Direct file writes to `solomon_brain_map.bin` without file path bounds verification inside serialize/deserialize routines.
- **Required next condition:** Add direct serialization, corruption, path-boundary, recall-quality, and restart tests.

### Mnemosyne Knowledge Cards Module
- **Path:** `core/solomon_knowledge_cards/`
- **Status:** PRESENT — UNPROVEN RUNTIME
- **Evidence:** Package exists and points to `solomon_soss.db`; the referenced core test suite is absent.
- **Claimed purpose:** A governed repository structure for managing episodic, factual, procedural, and warning memory cards, complete with status workflows, clearance scopes, and relationship graphing.
- **Runtime call sites:** `core/solomon_knowledge_cards/api/repository.py`
- **Storage:** `solomon_soss.db`
- **Known concern:** Schema validation allows arbitrary tag insertions without strict alphanumeric escaping.
- **Required next condition:** Prove runtime wiring, lifecycle transitions, retrieval, provenance, deduplication, and migrations.

### SQLite Database Manager
- **Path:** `core/solomon_knowledge_cards/storage/db.py`
- **Status:** PRESENT — PARTIAL
- **Evidence:** `DatabaseManager` exists with WAL/busy-timeout claims; it has no direct tests.
- **Claimed purpose:** Provides atomic card storage, SQLite connection factory with WAL mode, busy timeout, and automatic schema migrations.
- **Runtime call sites:** `core/solomon_knowledge_cards/api/repository.py`
- **Storage:** `solomon_soss.db` (or whatever db_path is supplied during initialization)
- **Known concern:** None (uses parameterization on SQL statements).
- **Required next condition:** Make it the single connection authority and add migration, concurrency, backup, restore, and integrity tests.

### Futures Dashboard Backend API
- **Path:** `backend/services/futures_dashboard_backend.py`
- **Status:** PRESENT — PARTIAL
- **Evidence:** Backend exists and `app.py` reportedly calls it; it writes to legacy `memory_atoms.db`.
- **Claimed purpose:** Serves projection outputs, receives executions, and binds presentation-level event metadata to candidate hashes.
- **Runtime call sites:** `app.py`
- **Storage:** `memory_atoms.db`
- **Known concern:** Allows direct submission of execute tasks without verifying signatures.
- **Required next condition:** Move it to canonical storage, add auth/signature checks, route tests, and outcome writeback.

---

## 6. Static or Unwired Interface Inventory

### God Eye Real-Time Dashboard UI
- **Path:** `templates/god_eye.html`
- **Status:** PRESENT — STATIC/UNWIRED
- **Evidence:** HTML exists but calls a backend route the registry says does not exist.
- **Current dependency:** Uses hardcoded `/api/memory/graph.json` route (not present on any backend Flask mapping)
- **Known concern:** Loads Three.js from external CDNs, creating potential XSS/CSP issues if unpinned.
- **Required next condition:** Do not call it live until the bridge, route, tests, stale-state handling, and provenance view exist.

### Futures Prediction Dashboard UI
- **Path:** `templates/futures_dashboard.html`
- **Status:** PRESENT — STATIC/UNPROVEN
- **Evidence:** HTML exists; no tests or runtime call site are recorded.
- **Current dependency:** None
- **Known concern:** Loads inline external CDNs.
- **Required next condition:** Add route/render tests, CSP, pinned dependencies, error states, and live backend proof.

---

## 7. Missing Component Inventory

| Missing component | Intended function | Existing substitute or note | Required decision |
| :--- | :--- | :--- | :--- |
| **Quantized Engine Budget & Efficiency Guard** (`core/solomon_quantized_efficiency.py`) | Intended to manage execution budget arrays and enforce T1-T5 tiers via memory-mapped budget tables. | We have `core/solomon_context_budgeter.py` instead, which implements basic token limits but not the claimed T1-T5 memory budget tables. | Decide whether to implement a measured budget layer or remove the unsupported claim. |
| **Resident Daemon Framework** (`core/swarm/resident_framework.py`) | Intended to provide the zero-copy memory-mapped checkpoint mechanism for background loops. | None | Implement one lifecycle/checkpoint/lease framework only after the direct learning loop works. |
| **Guardian Resident Daemon** (`services/solomon_guardian_resident.py`) | Intended to manage background telemetry, disk usage, and host checks in a continuous loop. | None | Implement bounded health, recovery, resource, and escalation duties on the canonical resident framework. |
| **Jules Resident Daemon** (`services/solomon_jules_resident.py`) | Intended to perform automated repository scans, duplicate checks, and validation proposals. | None | Implement repository convergence and validation work on the canonical resident framework. |
| **MD8 Testing & Verification Framework** (`services/solomon_validation_framework.py`) | Intended to provide O(1) slot hashing linear-probing index checks over a zero-copy memory substrate with fcntl locks. | None | Use a correct, testable validation framework first; optimize only after measurement. |
| **God Eye Bridge API** (`backend/services/god_eye_bridge.py`) | Intended to map 128-byte ternary memory embeddings into 3D semantic layout coordinates. | None | Implement the canonical memory graph endpoint and prove data lineage. |
| **Resident Daemon Dashboard API** (`backend/services/resident_dashboard.py`) | Intended to serve `/api/residents/status` and `/api/residents/messages` REST endpoints. | None | Build only after residents and checkpoints are real. |
| **Global Health & Telemetry Dashboard** (`backend/services/health_dashboard.py`) | Intended to serve global health metrics and telemetry analysis endpoints. | None | Expose real service, database, queue, checkpoint, backup, and failure status after lifecycle convergence. |
| **Hyper Registry Manager** (`core/solomon_hyper_registry.py`) | Intended to enforce O(1) semantic metadata constraints, DFS dependency cycles, and alphabetic loader rules. | None | Choose one simple canonical registry; add dependency and duplicate-registration tests before optimizing. |

### Missing-component priority

#### Priority 0 — Required for a real perpetual loop
- Resident Daemon Framework
- Guardian Resident
- Jules/Convergence Resident
- Canonical validation framework or equivalent

#### Priority 1 — Required for live visibility and control
- God Eye Bridge API
- Resident Dashboard API
- Global Health Dashboard
- Canonical component registry

#### Priority 2 — Add only after measurement
- Quantized T1–T5 budget/efficiency guard

---

## 8. State Store Inventory

The current architecture is fragmented across at least five state mechanisms.

| Store | Current evidence | Role now | Defect | Required disposition |
| :--- | :--- | :--- | :--- | :--- |
| `memory_atoms.db` | SQLite, 4 rows, journal delete, foreign keys 0, integrity ok | Legacy/test memory and several active component dependencies | No migrations, no isolation, duplicate empty lessons, root tests mutate it | Migrate to canonical DB or explicitly label as disposable test fixture |
| `solomon_soss.db` | Named by registry but not included in archive | Claimed knowledge-card/Futures canonical store | Existence, schema, data, backup, and runtime use not evidenced | Locate, inspect, version, and make canonical—or remove claim |
| `solomon_brain_map.bin` | Named by quantized-memory registry entry but not included | Claimed serialized quantized graph | No bounds, corruption, compatibility, or restart proof | Treat as derived cache until proven authoritative |
| `governance_log.bin` | 65,536 bytes; 116 non-zero bytes | Status-slot prototype | Not reconstructable, no packet metadata, overwrite/alignment risk | Replace or wrap with append-only structured governance events |
| `fact_memory.log` | One line: `[1785138971.8992364] Threshold 90.0 crossed with value 90.5` | Threshold event trace | No identity, provenance, outcome, retention, or replay structure | Move events into canonical structured event store; retain text log only as output |

### Current `memory_atoms.db` contents

| id | packet_id | memory_type | result | lesson |
| :--- | :--- | :--- | :--- | :--- |
| 1 | p1 | lesson | pass | ` ` |
| 2 | p1 | lesson | pass | ` ` |
| 3 | p1 | lesson | pass | ` ` |
| 4 | p1 | lesson | pass | ` ` |

*Note: All four rows are duplicates with an empty lesson. This is evidence of a fixture or incomplete writeback path, not cumulative learning.*

### Governance binary visible sequence
`refusedunknownapprovedunknownrefusedunknownapprovedunknownrefusedunknownapprovedunknownrefusedunknownapprovedunknown`

*The sequence records statuses but cannot independently reconstruct requests, reviewers, artifact hashes, risk, reasons, tests, rollback, or promotion.*

---

## 9. Test Inventory

The supplied baseline reports:
> 25 passed, 0 warnings, 3.36 seconds

| Test file | Tests represented by output | Primary area |
| :--- | :--- | :--- |
| `tests/futures/test_threshold_logic.py` | 5 | Futures Gate A/Gate B threshold logic |
| `tests/test_engine_registry.py` | 1 | Engine registry behavior |
| `tests/test_gabriel.py` | 10 | Gabriel models, permissions, loop, Flask endpoints |
| `tests/test_gabriel_evolution.py` | 4 | Gabriel evolution behavior |
| `tests/test_governance_approval.py` | 2 | Governance approval prototype |
| `tests/test_joe_blueprint_facade.py` | 1 | Blueprint facade |
| `tests/test_learning_writeback.py` | 1 | Learning writeback prototype |
| `tests/test_run_daily_scan.py` | 1 | Daily scan script |

### Test gaps
- No direct quantized-memory test file is present.
- The named knowledge-card core tests are absent.
- `DatabaseManager` has no direct tests.
- No canonical-database convergence test exists.
- No real retrieval-before-planning test is evidenced.
- No outcome-linked utility/confidence update test is evidenced.
- No resident lease, restart, checkpoint, or reboot test exists.
- No God Eye backend or graph-route test exists.
- No backup/restore test exists.
- No database concurrency or lock-contention test exists.
- No path traversal, symlink escape, unauthorized import, signature, or endpoint authorization tests are evidenced.
- No Futures outcome reconciliation or calibration test is evidenced.
- No production deployment smoke test is evidenced.

---

## 10. API and Interface Inventory

| Surface | Current status | Evidence | Missing proof |
| :--- | :--- | :--- | :--- |
| **Core Flask gateway** | Present in `app.py` | Gabriel endpoint tests reportedly pass | Production service lifecycle, auth, safe errors, health, restart |
| **Futures backend** | Present | Registry says `app.py` calls it | Signed/authorized execution, canonical DB, route tests, outcome reconciliation |
| **Learning writeback route** | Present | One test | Actor provenance, authorization, idempotency, validation and outcome linkage |
| **God Eye UI** | Static only | Template exists | Backend route, graph data, provenance, stale-state behavior, tests |
| **Futures UI** | Static/unproven | Template exists | Render/route tests, CSP, pinned dependencies, error states, and live backend proof |
| **Resident dashboard** | Missing | None | Residents, status endpoints, messages, tests |
| **Health dashboard** | Missing | None | Real health sources, failure states, tests |

---

## 11. Autonomous-Learning Loop Inventory

| Required link | Current evidence state |
| :--- | :--- |
| **Observe event/failure/correction** | Partial: logs and tests create events |
| **Create structured learning candidate** | Partial: writeback exists, but candidate schema and provenance are not proven |
| **Deduplicate candidate** | Failed: four duplicate empty p1 lessons exist |
| **Validate candidate** | Unproven as one canonical lifecycle |
| **Governance decision** | Prototype only; status slots are insufficient |
| **Activate canonical memory** | Knowledge-card package exists, live activation not proven |
| **Index memory** | Quantized memory exists, canonical linkage is unproven |
| **Retrieve before planning** | Not evidenced end to end |
| **Apply memory to execution** | Not evidenced end to end |
| **Measure outcome** | Partial in isolated tests; no canonical trace |
| **Update confidence/utility/content** | Writeback prototype exists; outcome linkage unproven |
| **Select next learning target** | Not evidenced |
| **Execute bounded learning work** | Gabriel lab exists; governed promotion not proven |
| **Checkpoint and repeat** | Resident framework missing |
| **Survive process restart/reboot** | Not evidenced |

### Closed-loop verdict
The repository contains several pieces of a learning system, but the complete loop is not yet proven. The most important next test remains one end-to-end `test_real_perpetual_learning_cycle` that crosses all stages without manual database editing.

---

## 12. Security and Governance Inventory

| Area | Existing element | Current risk/gap |
| :--- | :--- | :--- |
| **Dynamic capabilities** | Gabriel loader and AST-related experiments | Compromised directories may allow unsafe dynamic imports or path traversal |
| **File serialization** | Quantized binary graph | No proven path bounds, symlink protection, corruption detection, or compatibility version |
| **Governance** | Approval lane and binary status log | Not reconstructable; offset drift and partial-write risk |
| **Learning writeback** | REST/local writeback path | No strong actor identity, signature, or provenance |
| **Futures execution** | Dashboard backend accepts execute tasks | Registry says signatures are not verified |
| **Web gateway** | Flask app | Debug tracebacks may expose internals |
| **Frontend dependencies** | External CDNs and inline dependencies | CSP, pinning, integrity, and offline reliability not proven |
| **Production promotion** | Claimed governance concept | No SS2→SS3→SS1 evidence packet in archive |

---

## 13. Deployment Inventory

| Deployment requirement | Evidence state |
| :--- | :--- |
| **Sandbox execution** | Reported |
| **Production-like service command** | Not included |
| **systemd/supervisor/container service definition** | None reported |
| **Health endpoint capture** | Not included |
| **Active process/socket capture** | Not included |
| **Start on reboot** | Not proven |
| **Process restart recovery** | Not proven |
| **Host reboot recovery** | Not proven |
| **Log retention** | Not proven |
| **Backup schedule** | Absent |
| **Restore drill** | Not proven |
| **SS3 independent review** | Not proven |
| **SS1 promotion** | Not proven |

---

## 14. Canonicalization Decisions Required

The following decisions must be made before adding more major subsystems:
1. **Canonical database**: `solomon_soss.db` or a replacement—never multiple undocumented production authorities.
2. **Canonical connection factory**: One tested owner for WAL, busy timeout, foreign keys, migrations, backups, and test isolation.
3. **Canonical memory lifecycle**: One schema and status flow for candidates, validation, activation, retrieval, usage, outcomes, confidence, and utility.
4. **Canonical component registry**: Use the existing tested engine registry if suitable, or replace it deliberately; do not create another competing registry.
5. **Canonical lifecycle manager**: One owner for startup, shutdown, signals, residents, checkpoints, API, and health.
6. **Canonical governance record**: Structured, append-only, tamper-evident, reconstructable decisions.
7. **Canonical environment roles**: SS2 development, SS3 independent validation, SS1 governed production.

---

## 15. Priority Work Inventory

### P0 — Truth and data integrity
- Correct the master audit so missing components are not described as active.
- Commit a clean evidence checkpoint.
- Locate and inspect `solomon_soss.db`.
- Choose one canonical production store.
- Isolate tests from root/production state files.
- Stop duplicate empty memory writes.
- Add schema migrations, provenance, idempotency, backup, and restore.

### P1 — Complete the learning loop
- Implement one real event-to-reuse-to-outcome trace.
- Add candidate validation and governance transitions.
- Prove retrieval occurs before planning.
- Prove memory influences the second execution.
- Update memory utility/confidence from the outcome.
- Select the next learning target.

### P2 — Continuity and safe autonomy
- Implement one resident framework.
- Add durable checkpoints and leases.
- Implement Guardian and convergence/learning duties.
- Prove restart and reboot recovery.
- Add bounded permissions, resource budgets, rollback, and escalation.

### P3 — Security and governance
- Harden dynamic loading and paths.
- Authenticate/authorize execution and writeback routes.
- Build reconstructable governance packets.
- Add tamper, corruption, concurrency, and negative security tests.

### P4 — Live interfaces
- Implement God Eye backend only after canonical memory works.
- Add resident and health dashboards only after real residents exist.
- Connect Futures UI to canonical data and outcome reconciliation.

### P5 — Measured efficiency
- Establish baselines before building the missing quantized-efficiency guard.
- Optimize measured bottlenecks.
- Require quality parity and rollback for each quantized path.

---

## 16. Inventory Completion Matrix

| Domain | Current condition | Evidence-backed completion |
| :--- | :--- | :--- |
| **Repository identity** | Partial | Repository/branch/commit reported; full source not included and tree dirty |
| **Core tests** | Partial-positive | 25 passed, but coverage is narrow and warnings remain |
| **Storage** | Failed convergence | Multiple stores and no proven canonical authority |
| **Memory lifecycle** | Partial | Knowledge-card and writeback code exist; end-to-end lifecycle unproven |
| **Retrieval** | Partial/unknown | Quantized memory exists; retrieval-before-planning trace absent |
| **Outcome learning** | Partial/unknown | Isolated writeback exists; measured reuse trace absent |
| **Autonomous residents** | Missing | Framework and resident files absent |
| **Governance** | Prototype | Two tests, but evidence log cannot reconstruct decisions |
| **Capability acquisition** | Tested laboratory | Gabriel tests pass; security and promotion controls incomplete |
| **Futures/Loki** | Tested threshold core | Outcome reconciliation and calibration absent |
| **God Eye** | Static prototype | UI exists; live bridge missing |
| **Health/telemetry** | Missing | No health dashboard or resident status service |
| **Production deployment** | Not proven | Sandbox only, no service manager or restart/reboot proof |
| **Backup/restore** | Missing | No automated backup or restore validation |
| **Security hardening** | Failed claim | Multiple known unresolved risks |
| **Perpetual learning** | Not proven | Closed loop and continuity are incomplete |

---

## 17. What Can Be Reused

Do not throw away the present core. The following are candidates for convergence and hardening rather than replacement:
- `app.py` as a possible gateway shell.
- Gabriel capability tests and core pipeline.
- Futures threshold logic and its tests.
- Knowledge-card model/repository concepts.
- `DatabaseManager` as a possible canonical connection layer.
- Learning writeback as a starting adapter.
- Governance approval API shape, while replacing its evidence storage.
- Existing engine registry, if it can become the one canonical registry.
- Quantized memory as a derived index/cache after correctness and provenance are established.
- Existing dashboard templates after their backend truth sources exist.

---

## 18. Items That Must Not Be Counted as Complete

- A file existing without a runtime call site.
- A static dashboard without a live backend.
- A passing unit test that mocks the closed loop.
- A binary file containing only status strings.
- Duplicate pass rows with empty lessons.
- A CLI script without a scheduler or resident.
- A sandbox process without restart/reboot proof.
- A named database that is not included, inspected, migrated, backed up, and restored.
- An optimization claim without before/after quality and resource measurements.
- A maturity level based on narrative descriptions instead of acceptance traces.

---

## 19. Next Inventory Update Trigger

Produce the next inventory only after the repository supplies new evidence for at least one of these:
- clean checkpoint commit
- canonical database migration
- real closed-loop test
- resident restart proof
- governance packet reconstruction
- security test expansion
- production deployment evidence
- backup and restore drill

*The next inventory must compare evidence item by item against this baseline rather than resetting the status language.*

---

## 20. Final Inventory Summary

Project Solomon currently has a meaningful tested foundation, especially in Gabriel, Futures threshold logic, the gateway, governance prototype, and learning-writeback prototype. The repository also appears to contain knowledge-card and quantized-memory foundations.

The central problem is no longer a total absence of code. The central problem is convergence and proof:
- multiple state authorities
- incomplete memory lifecycle
- missing residents
- static dashboards without live truth sources
- incomplete governance evidence
- unresolved security boundaries
- no restart-safe autonomous loop
- and no single end-to-end trace proving that Solomon learns something, reuses it, improves, selects the next target, and continues.

*That is the exact inventory baseline from which the next build should proceed.*
