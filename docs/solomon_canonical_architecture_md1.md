# Project Solomon

# Phase 1 — Architectural Convergence

## Engineering Specification MD1

### The Canonical Solomon Architecture

> **Status:** Draft 1.0
> **Primary Implementer:** Jules
> **Review:** Joe

## Mission

Transform the current Solomon SOSS inventory into one unified architecture capable of supporting a governed perpetual learning machine.

This specification establishes the architectural laws every future subsystem must follow, enforcing a "Hyper-Efficiency Doctrine" that pushes algorithmic efficiency to theoretical limits through advanced structures like Zero-Copy Memory Substrates, 1-Bit Holographic Quantization, and Gödels Incompleteness Escapes.

## Current Canonical Systems

-   **Gabriel Engine** — Capability acquisition, evaluation (Crucible), optimization, and dynamic assimilation. Quarantine for SS2 laboratory work.
-   **Project Mnemosyne** — Durable governed memory, semantic ranking, reflection, and evidence ledger via SQLite (`solomon_soss.db`).
-   **Project Prometheus** — Dynamic planning, curiosity, task auditing, bottleneck-selection, and experiment selection.
-   **Unified Flask Gateway** — External API, routing, RAG injection, and unified gateway logic running strictly on Port 18789.
-   **Worker Runtime** — Background execution via `jules_resident`, `solomon_guardian`, bounded work packets, and thread-safe execution layers.
-   **Browser Companion** — Browser interaction and interaction telemetry gathering via debounced, bounded context extraction.
-   **Solomon API Registry** — Capability discovery strictly enforced via `solomon_api/engine_registry.json`.
-   **SS1 / SS2 / SS3 Governance** — Promotion and validation via `solomon_governance_approval_packet.py`, requiring explicit human gate (e.g., Mark's approval).

## Engineering Laws

1.  **One subsystem, one responsibility.** Every module has a distinct and strictly defined cognitive or architectural purpose.
2.  **One source of truth.** All systems share the unified state space `solomon_soss.db`, using thread-safe singleton managers (`DatabaseManager`).
3.  **Interfaces before implementation.** Contract boundaries must be absolute, validated structurally before any computation payload is initiated.
4.  **Everything measurable.** Learning and resource consumption must be quantified using O(1) memory bounds and strict cycle limits.
5.  **Every solved problem becomes permanent knowledge.** Verified successes are packaged as artifacts and merged into Mnemosyne for future retrieval.
6.  **Efficiency is a feature.** All primary throughput buffers must utilize zero-copy memory-mapping (`mmap`), 64-byte L1-cache alignment, and algorithmic limits (`__slots__`).
7.  **Quantization before expansion.** Engines operate within strict Tier and SizeClass enums (e.g., `T1_deterministic_for_dry_run`, `T5_human_gate`) and budget thresholds defined by `QuantizedEngineBudget`.
8.  **Architecture before implementation.** No feature surface expansion until foundational components are codified, wired, and tested.
9.  **Governance before autonomy.** Silent mutations in production (SS1) are explicitly blocked. Changes require SS3 gating and governed approvals (e.g., Phase 7 Governance Gate Integration).
10. **Every subsystem improves the next subsystem.** A Perpetual Learning Architecture where each cycle's feedback scoring loops back to policy adjustments.
11. **Gödels Escape.** The system incorporates meta-reasoning via state hashing (`solomon_goedel_escape.py`) to detect unprovable execution loops and force paradigm shifts when stuck.

## Canonical Architecture

### Component Hierarchy

```text
Infrastructure ↓
    |__ Unified State Space (`solomon_soss.db`, Zero-copy stores like `solomon_q_store.bin`)
    |__ Thread-safe connection managers, WAL-mode SQLite
    |__ Memory-mapped struct buffers for high-speedIPC
Core Runtime ↓
    |__ Unified Flask Gateway (Port 18789, Pattern B HTTP Facades)
    |__ O(1) ThreeBoxQueue (SS123 Queues)
    |__ Resident Framework (Guardian, Jules Daemons)
Cognitive Systems ↓
    |__ Prometheus (Planner, Task Safeties, Bottleneck Arbitration)
    |__ Mnemosyne (Episodic, Knowledge, and Skill Memory Substrate)
Learning Systems ↓
    |__ Gabriel Lab (Capability Assimilation, Crucible Validation)
    |__ SOSS Memory Writeback (QResultVerifier)
    |__ Nash Swarm Negotiation (Resource Contention Resolution)
Governance ↓
    |__ Governance Approval Lane (`governance_log.bin`)
    |__ Model Weight Supervisor
    |__ Gatekeepers (SS3 Validation, Explicit User Overrides)
External Interfaces
    |__ SOSS Workspace / Cognitive Interface (Port 18789)
    |__ Solomon Browser Companion Target Routes
    |__ Edge Proxy Routes (Port 7420 integration)
```

## Ownership Matrix

| System Component | Owner Subsystem | Canonical File/Module Core | Primary Responsibility |
| --- | --- | --- | --- |
| **API Gateway** | Unified Flask Gateway | `app.py`, `backend/services/` | Single entry point, proxy integrations, standard REST responses. |
| **Memory / SOK** | Project Mnemosyne | `core/solomon_knowledge_cards/` | Durable evidence ledger, semantic recall, persistent context. |
| **Planning & Arb**| Project Prometheus | `gabriel_engine/core/` (DynamicPlanner)| Curiosity queue, experiment boundary framing, tool orchestration. |
| **Skill Labs** | Gabriel Engine | `lab/solomon_q_engine.py`, SS2 code | Experimental code execution, AST injection, Crucible evaluation. |
| **Worker Threads**| Resident Daemons | `services/solomon_jules_resident.py` | Asynchronous work execution, bounded packet handling. |
| **Governance** | Governance Gates | `services/solomon_governance_approval_packet.py` | Enforcing strict approval logs and review requirements for SS1 changes. |
| **Registry** | Engine Registry | `solomon_api/engine_registry.json` | Explicit capability mapping, readiness status for all modules. |

## Interface Standards

1.  **Strict Bounding:** All internal communications and packet models (`WorkPacket`, `KnowledgeCard`) must use `__slots__` for deterministic memory footprint.
2.  **Memory-Mapped IPC:** Inter-process and daemon state synchronization MUST use zero-copy `mmap` with fixed-size `struct` buffers. When encoding strings, use byte-level padding (`payload.encode('utf-8')[:64].ljust(64, b'\x00')`) and safely strip nulls on decode. Hashed string IDs must be securely bitmasked (`& 0xffffffff`).
3.  **Namespace Isolation (Pattern B):**
    - `backend/services/` holds strictly HTTP-safe facades.
    - `services/` contains raw, control-plane root engines.
    - Dangerous root engines MUST NOT be directly imported by the web layer without dry-run/approval proxies (e.g., `joe_blueprint_facade.py`).
4.  **Absolute Paths & Validation:** Dynamically generated paths in AST Injectors or execution handlers must undergo strict absolute path traversal verification.
5.  **Timezone Compliance:** Absolute date/time values must use timezone-aware constructions (e.g., `datetime.datetime.now(datetime.UTC)`). No bare `utcnow()` deprecations.

## Integration Rules

1.  **State Unification:** A single database connection (`solomon_soss.db`) must be used for knowledge storage, leases, and memory writebacks, avoiding isolated fragmented stores (unless purely experimental in Gabriel's SS2 lab).
2.  **SS1/SS2/SS3 Transitions:**
    - **SS2 (Laboratory):** Gabriel explores, writes unverified dynamic code, and tests in Crucible.
    - **SS3 (Review):** Automated and human governance gates evaluate evidence, structure, safety, and reproducibility.
    - **SS1 (Production):** The approved artifact is promoted to a read-only execution state where it can be queried by Mnemosyne and utilized by Prometheus.
3.  **Initialization Sequencing:**
    - Background resident daemons must initialize safely with a threading lock (`_residents_started`) in `backend/main.py`.
    - Flask daemon managers (e.g., `NashSwarmManager`) require lazy initialization (evaluated at request runtime) to ensure they do not hang unit test suites during static import.
4.  **Codex Packet Discipline:** Any new feature must be Bounded, Named, Wired, Remembered, Tested, Governed, Resumable, and Efficient (The 8 Criteria).

## Architecture Review Checklist

*   [ ] Does the proposed subsystem fall entirely under a single Owner Subsystem?
*   [ ] Is the module's presence correctly declared in `solomon_api/engine_registry.json` and documented?
*   [ ] Does the codebase adhere to Pattern B Namespaces (no raw engines exposed to HTTP directly)?
*   [ ] Does it utilize zero-copy logic (`mmap`), `__slots__`, or Quantized boundaries for internal processing throughput?
*   [ ] Are mutations bounded by the Governance Approval Lane and explicitly logged?
*   [ ] Is the state persisted strictly into the unified database manager?
*   [ ] Does it avoid creating novel feature surface area prior to consolidating existing systems?
*   [ ] Are dynamic path generations securely gated against traversal exploits?
*   [ ] Does it run perfectly within a dry-run scope before transitioning into `T5_human_gate` execution?

## Definition of Done

Phase 1 MD1 is complete when Project Solomon has one agreed architectural foundation that all future engineering work must follow. The file `solomon_canonical_architecture_md1.md` stands as the indisputable structural law for all further perpetual learning implementations.