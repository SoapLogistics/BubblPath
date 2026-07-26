# Project Solomon: Canonical Architecture

**Status:** Draft 1.0 (Extreme Efficiency Edition)
**Primary Implementer:** Jules
**Review:** Joe

## Mission
Transform the current Solomon SOSS inventory into an ultra-unified, zero-copy, O(1) architecture capable of supporting a strictly governed perpetual learning machine. This architectural convergence pushes performance to the theoretical limits, embedding quantal computing efficiencies, Gödel incompleteness escapes, and purely deterministic orchestration into the foundation.

## Engineering Laws (Extreme Efficiency Doctrine)

1.  **One subsystem, one responsibility:** O(1) isolated deterministic bounds.
2.  **One source of truth:** Unified `solomon_soss.db` accessed entirely through zero-copy `mmap` where applicable, with thread-safe `RLock` protections.
3.  **Interfaces before implementation:** API boundaries strictly typed with `__slots__` and fixed-size byte structures.
4.  **Everything measurable:** Every tick recorded deterministically for the Continuous Perpetual Learning Loop.
5.  **Every solved problem becomes permanent knowledge:** Memory writebacks enforce Q-Result Verification, logging outcomes to `memory_atoms`.
6.  **Efficiency is a feature:** O(1) Swarm routing via `mmap` ThreeBoxQueues, 64-byte L1-cache aligned Swarm Negotiation buffers.
7.  **Quantization before expansion:** All runtimes adhere to 1-Bit Holographic Quantization, prioritizing deterministic Dry Runs (Tier 1).
8.  **Architecture before implementation:** Immutable namespace partitioning (`services/` strictly for Engines, `backend/services/` for Facades).
9.  **Governance before autonomy:** Zero mutations occur without absolute Governance Gates (SS3 review, Mark Approval).
10. **Every subsystem improves the next subsystem:** Perpetual execution loops must run on continuous deterministic feedback cycles (The Resident Framework).
11. **Total Algorithmic Maximum:** Gödels Incompleteness Escapes actively monitor for structural lockups.

## Canonical Architecture (The Stack)

- **Infrastructure:**
  - Zero-Copy Memory Substrate (`governance_log.bin`, `signal_log.bin`)
  - Unified `solomon_soss.db` with Threading Locks (`RLock`)
- **Core Runtime:**
  - Quantized Engine Budget / `RuntimeGuardrails`
  - Resident Framework (Guardian & Jules Daemon Loops)
- **Cognitive Systems:**
  - Project Mnemosyne (Governed Long-Term Memory / Cards)
  - Project Prometheus (Planning / Auditing)
- **Learning Systems:**
  - Gabriel Engine (Capability Acquisition and Clean-Room Lab)
  - QResultVerifier (Memory Atoms / Pass-Fail Verification)
- **Governance:**
  - SS1/SS2/SS3 ThreeBoxQueues (O(1) Route-and-Review System)
  - Solomon Governance Approval Packet
- **External Interfaces:**
  - Unified Flask Gateway (Port 18789)
  - Node.js Edge Proxy (Port 7420)
  - Solomon Browser Extension (Debounced Context Extraction)

## Ownership Matrix

| Subsystem | Core Component | Canonical Owner | File / Namespace Rule | Status |
|---|---|---|---|---|
| Memory Engine | Project Mnemosyne | Jules Resident | `core/solomon_knowledge_cards/` | Governed, Read/Write |
| Evolution Engine | Gabriel Engine | Gabriel Protocol | `gabriel_engine/` | Quarantined Sandbox |
| Reasoning & Planning | Project Prometheus | Jules Resident | `core/solomon_context_budgeter.py` | Governed |
| Gateways / Routing | Unified Flask App | Gateway Controller | `app.py` (Port: 18789) | Unified Route Pool |
| Active Runtimes | Worker Daemons | Soloman Resident | `backend/main.py` (Flag: `_residents_started`) | Thread-Safe Daemon |
| SOSS DB Pool | DB Manager | Shared (Thread-Safe) | `gabriel_engine/core/models.py` | Single Data Truth |
| Governance Logic | Approval Packets | JOE / Governance | `services/solomon_governance_approval_packet.py` | Mandatory Pass/Fail |

## Interface Standards

1.  **Memory Layout:** Inter-process communication operates on fixed-sized C-struct `struct` boundaries aligned for 64-byte L1 cache efficiency.
2.  **State Hashing:** Continuous determinism is mandated. SHA-256 or Murmur3 non-cryptographic hashes are required for context diffs.
3.  **Strict Typing:** Python structures carrying memory allocations must use `__slots__` exclusively.
4.  **No Anonymous Engines:** All Python modules acting as engines under `services/`, `solomon_api/`, and `backend/services/` must be explicitly listed in `solomon_api/engine_registry.json`. Status classes must strictly track states like `active_readiness` for background tasks, and `active_route` for API-exposed modules.
5.  **Proxy Facades:** Root engines with dangerous behavior (e.g. `services/solomon_joe_bridge.py`) are permanently isolated from the HTTP server via strict routing patterns. The Flask app may only import from `backend/services/`.
6.  **Path Normalization:** Forward slashes `/` are strictly enforced for cross-platform URI definitions and module tracking.
7.  **Concurrency Guards:** All SQLite interactions in the shared knowledge store utilize `threading.RLock()` to permit lock-safe memory loops without collision.

## Integration Rules

-   **O(1) Unification:** All feature APIs must route back to the Unified Gateway (`app.py`) on port 18789. The `solomon_api/engine_registry.json` dictates availability.
-   **Swarm Routing:** Operations executing outside single thread scope must dispatch to Swarm Blueprints using the Nash Equilibrium Protocol (`mmap` optimized).
-   **Zero Side Effects (Test Independence):** Modules must safely bypass initialization of execution daemons (e.g. Loki, Resident) when imported by test suites. Testing evaluates code deterministically with isolated module connections.
-   **Governance Gates:** Any state mutation aiming for SS1 Promotion must encode an explicit `Mark Approval` trace inside the structured governance binary logs (`governance_log.bin`).
-   **Gödel Escapes:** Continuous daemon loops implement logic hashes. If hash sequences repeat endlessly, a paradigm-shift fault is synthesized.

## Architecture Review Checklist

- [ ] Does the subsystem possess exactly one operational responsibility?
- [ ] Is it bound strictly to the `solomon_soss.db` thread-safe pool?
- [ ] Are its models fully O(1) optimized (utilizing zero-copy `mmap` or `__slots__`)?
- [ ] Has it been registered in the Engine Registry (`solomon_api/engine_registry.json`)?
- [ ] Is dangerous capability safely restricted to the Quarantine Lab (Gabriel) without exposing the Gateway?
- [ ] Does the engine report telemetry into the Perpetual Learning loop?
- [ ] Are structural bounds (namespaces, memory buffers, dependency imports) adhered to?

## Definition of Done
Phase 1 MD1 is complete. Project Solomon operates under one absolute architectural foundation designed for maximum computational velocity and hyper-efficient perpetual learning.
