# Canonical Solomon Architecture

## 1. Overview
The Canonical Solomon Architecture establishes the structural foundation for a governed perpetual learning machine. This document dictates the rigid separation of concerns, the flow of data, and the specific technological constraints required to maximize algorithmic efficiency and ensure safe autonomous operation.

## 2. Engineering Laws
1. **One subsystem, one responsibility:** No overlapping concerns (e.g., memory and planning remain strictly separate).
2. **One source of truth:** A single SQLite ledger (`solomon_soss.db`) combined with zero-copy memory-mapped logs.
3. **Interfaces before implementation:** API contracts and struct schemas dictate module interactions.
4. **Everything measurable:** Core systems emit latency, budget, and memory metrics natively.
5. **Every solved problem becomes permanent knowledge:** Discoveries promote to versioned skill packages, not transient memory.
6. **Efficiency is a feature:** Use zero-copy memory-mapped files (`mmap`), fixed-size struct buffers, and bounded quantization.
7. **Quantization before expansion:** Restrict runtime execution via tiered budgets (e.g., `T1_deterministic_for_dry_run`).
8. **Architecture before implementation:** Designs must pass the review checklist before coding begins.
9. **Governance before autonomy:** All mutations to SS1 require explicit approval and cryptographic hashes.
10. **Every subsystem improves the next subsystem:** Telemetry from Gabriel informs Prometheus, which in turn feeds Mnemosyne.

## 3. Layered Architecture

### 3.1 External Interfaces
* **Unified Flask Gateway (`app.py`):** The single entry point for all API traffic (running on port `18789`).
* **Browser Companion:** The debounced, bounded-context interaction point bridging the web and Solomon.
* **Backend Facades (`backend/services/`):** "Pattern B" dictates these are HTTP-safe proxies. They never contain raw execution logic.

### 3.2 Governance & Security
* **SS1 / SS2 / SS3 Roles:** Strict separation of Production, Sandbox, and Gatekeeper environments.
* **Governance Approval Lane:** Memory-mapped binary logs (`governance_log.bin`) tracking cryptographic hashes and manual approvals for high-risk actions.
* **Gödels Incompleteness Escapes:** Meta-reasoning engines forcing paradigm shifts during unprovable execution loops.

### 3.3 Learning Systems
* **Mnemosyne (Memory System):** The governed cognitive substrate managing episodes, lessons, and persistent evidence, stored efficiently via SQLite and serialized payloads.
* **Prometheus (Planning System):** The deterministic task planner leveraging historical successes/failures.
* **Gabriel (Skill Acquisition):** A quarantined, sandbox laboratory (SS2) for evaluating, reconstructing, and validating new executable skills via Crucible testing.

### 3.4 Cognitive Systems & Core Runtime
* **J.O.E. & Resident Daemons:** Continuous execution loops leveraging thread-safe `RLock` connections, mmap state tracking, and background learning threads.
* **Nash Equilibrium Swarm:** Resource contention resolution using zero-copy 64-byte L1-cache aligned memory maps.
* **Q Blueprint Store:** `O(1)` memory-mapped `ThreeBoxQueue` routing.

### 3.5 Infrastructure Substrate
* **Unified SQLite Store (`solomon_soss.db`):** WAL-enabled unified relational data.
* **Zero-Copy Memory-Mapped Files (`*.bin`):** `signal_log.bin`, `solomon_q_store.bin` for cross-process, high-frequency state updates.

## 4. Architectural Dictates
* **No dynamic root imports:** The API gateway must never directly import dangerous execution engines from the root `services/` directory.
* **Engine Registry Compliance:** Every active capability must be statically registered in `solomon_api/engine_registry.json`.
* **Zero-Copy Serialization:** Internal high-frequency IPC must use struct byte packing with explicit unsigned integer packing (`I`) or null-byte stripped UTF-8 strings.
