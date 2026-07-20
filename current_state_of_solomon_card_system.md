# Current State of Solomon Card System

## Executive Summary
Through thorough reverse-engineering of the **Solomon / OpenClaw operating workspace** and surrounding architectural blueprints, we have documented the existing card-based protocol ecosystem. This system codifies operational doctrine, autonomy rules, and self-evolution procedures.

While the small Flask application (`app.py`) serves as a stateless gateway, the actual autonomy workspace is defined by a modular, document-driven architecture. This document provides a complete breakdown of the existing card architecture, the lifecycle of these cards, and the distinction between theoretical specs and active code implementations.

---

## 1. Discovered Card Types & Ecosystem

In the Solomon ecosystem, **"Cards"** are structured units of instruction, work, or knowledge. Rather than a simple, monolithic memory database, the system is evolving toward a complete card-oriented operating system, where cards act as Solomon's core operating language.

These cards are categorized into the following distinct families:

| Card Family | Format / Representation | Purpose / Core Question Answered |
| :--- | :--- | :--- |
| **Identity Cards** | `IDENTITY.md`, `SOUL.md` | "Who am I?" Core behavioral traits, alignment guardrails, and operational boundaries of Solomon. |
| **Mission Cards** | Workspace metadata / target goals | "Why are we doing this?" High-level strategic and directional objectives. |
| **Procedure Cards (PC)** | `checklists/*` or PC-SO-XX schemas | "How do we normally do this?" Standardized, reusable playbooks (e.g., `PC-SO-01`, `PC-SO-02`) that guide high-level agent routines. |
| **Task Cards** | Queue Task JSON / `autonomous_cycle.md` | "What exactly should happen this time?" Units of execution representing individual steps, inputs, and targeted outputs for workers. |
| **Review Cards / Packets** | SS3 Review Schema JSON | Evaluation packages used to assess worker performance and validate lessons before codification. |
| **Knowledge Cards** | Synthesis templates | "What permanent thing did we learn?" Codified insights generated from executions, failures, and decisions. |
| **Failure Cards** | Post-task reflection logs | "What went wrong?" Documented bugs, timeouts, or logical failures during execution. |
| **Repair Cards** | Remediation playbooks | "How do we fix it?" Proven recovery procedures for specific failures. |
| **Skill Cards** | Tool & Prompt profiles | "What are our specialized capabilities?" Capability and tool definition specs. |
| **Decision Cards** | ADRs (Arch Decision Records) | "What did we decide and why?" Design rationale and engineering choices. |
| **Architecture Cards** | System schemas & topologies | "How is the system structured?" Structural bounds and interaction protocols. |

---

## 2. Evolution of the Card System
The card system has evolved through three distinct evolutionary stages:

1.  **Stage 1: The Task Card (Ephemeral State):**
    *   *Origin:* Simple JSON instructions pushed to a queue.
    *   *Characteristics:* High granularity, single-use, stateless, and focused on executing a brief discrete command.
2.  **Stage 2: Operational Checklists (Document-Driven Doctrine):**
    *   *Origin:* Transitioning checklists into active Markdown-based operating rules (`autonomous_cycle.md`, `openhands_integration.md`).
    *   *Characteristics:* Human-readable, structured, but decoupled from runtime execution engines.
3.  **Stage 3: The Procedure-Card Factory (Automated Synthesis):**
    *   *Origin:* `solomon_procedure_card_factory.py`.
    *   *Characteristics:* Programmatic generation, semantic indexing (`solomon_procedure_index.json`), and structured versioning enabling Solomon to dynamically package, parameterize, and write its own procedures.

---

## 3. Discovered Card Schemas & Fields

### A. Procedure Card (PC) Schema (e.g., PC-SO-01, PC-SO-02)
Procedure cards represent Solomon's reusable operational playbooks:
```json
{
  "procedure_id": "PC-SO-XX",
  "title": "String",
  "domain": "Enum (COGNITION, SYSTEM_EVOLUTION, INTEGRATION, ABSORPTION)",
  "version": "SemanticVersion",
  "dependencies": ["Array of Procedure IDs"],
  "trigger": {
    "type": "Enum (CRON, EVENT, MANUAL)",
    "condition": "String"
  },
  "steps": [
    {
      "step_number": "Integer",
      "action": "String",
      "required_tools": ["Array of Tool Names"],
      "expected_outcome": "String"
    }
  ],
  "telemetry": {
    "metrics_file": "String (e.g., 'growth_metrics.json')",
    "logs_file": "String (e.g., 'heartbeat.log')"
  }
}
```

### B. Task Card Schema
Task cards dictate individual runs dispatched to worker agents:
```json
{
  "task_id": "UUIDv4",
  "parent_procedure": "String (PC-SO-XX)",
  "agent_role": "String (e.g., 'OpenSourceAbsorber')",
  "inputs": {
    "target_repository": "String",
    "absorb_depth": "Integer"
  },
  "guardrails": {
    "max_iterations": "Integer",
    "timeout_seconds": "Integer"
  }
}
```

---

## 4. The Closed Learning Loop: Card Flow & Cognitive Cycle
The flow of intelligence through Solomon is a circular learning system, transforming raw execution events into permanent, governed procedural intelligence:

```
                      ┌──────────────────────────────────────┐
                      │             Mission Card             │
                      │       ("Why are we doing this?")     │
                      └──────────────────┬───────────────────┘
                                         ▼
                      ┌──────────────────────────────────────┐
                      │            Procedure Card            │
                      │     ("How do we normally do this?")  │
                      └──────────────────┬───────────────────┘
                                         ▼
                      ┌──────────────────────────────────────┐
                      │              Task Card               │
                      │     ("What should happen this time?")│
                      └──────────────────┬───────────────────┘
                                         ▼
                      ┌──────────────────────────────────────┐
                      │            Worker Report             │
                      │         ("What actually happened?")  │
                      └──────────────────┬───────────────────┘
                                         ▼
                      ┌──────────────────────────────────────┐
                      │            Review Packet             │
                      │             (SS3 Governance)         │
                      └──────────────────┬───────────────────┘
                                         ▼
                      ┌──────────────────────────────────────┐
                      │            Knowledge Card            │
                      │     ("What permanent thing learned?")│
                      └──────────────────┬───────────────────┘
                                         ▼
                      ┌──────────────────────────────────────┐
                      │           Procedure Update           │
                      │     (Refining the operational loop)  │
                      └──────────────────────────────────────┘
```

1.  **Mission Ingestion:** High-level strategizing establishes a *Mission Card* (Why).
2.  **Procedure Mapping:** The system retrieves or drafts the corresponding *Procedure Card* (How).
3.  **Task Dispatch:** The *Task Card* is generated (What) and queued.
4.  **Worker Execution:** The worker processes the task, yielding a *Worker Report*.
5.  **Governance & SS3 Review:** The run is evaluated and documented in a *Review Packet*.
6.  **Knowledge Distillation:** Core insights, successes, or failures are codified into a *Knowledge Card*.
7.  **Loop Closure:** The updated knowledge is dynamically folded back into the *Procedure Card*, optimizing the loop for future runs.

---

## 5. Short-Term State vs. Long-Term Knowledge
We distinguish between short-term state vectors and long-term operating parameters:

*   **Short-Term State (Ephemeral & Dynamic):**
    *   *Components:* Active Queue Tasks, Worker Reports, current process PIDs, `heartbeat.log` updates.
    *   *Purpose:* Tracks execution context, immediate progress, and transient system states. Discarded or summarized once the task terminates.
*   **Long-Term Knowledge (Static & Persistent):**
    *   *Components:* Identity and Soul files (`IDENTITY.md`, `SOUL.md`), Procedure Cards, `solomon_oss_first_pass_registry.json`.
    *   *Purpose:* Guides overarching behavior, safety limits, architectural rules, and standardized execution playbooks across multi-day lifecycles.

---

## 6. Documented Maturity Matrix

The card system has established a powerful operating framework. We map the verified implementation against planned capabilities below:

| Layer | Status | Description |
| :--- | :--- | :--- |
| **Operational Doctrine** | ✅ Mature | Core markdown identity/checklist doctrine exists and guides agent cycles. |
| **Procedure-card framework** | ✅ Implemented | Standard operating templates (e.g., `PC-SO-01`, `PC-SO-02`) exist in the workspace. |
| **Identity/alignment system** | ✅ Implemented | Core `IDENTITY.md`, `SOUL.md`, and `USER.md` instructions loaded by agents. |
| **Card Lifecycle** | ✅ Defined | Multi-stage lifecycle (Mission → Procedure → Task → Worker → Review → Knowledge). |
| **Procedure Factory** | 🟡 Partially Implemented | Code utility capable of programmatically instantiating card templates. |
| **Runtime Orchestration** | 🟡 Partially Implemented | Queue and run orchestration exists but requires tighter semantic tie-ins. |
| **Semantic Retrieval** | 🔴 Planned | Real-time hybrid search/vector embedding-driven retrieval prior to task runs. |
| **Reflection Engine** | 🔴 Planned | Post-task automated log parser designed to generate new Failure and Repair cards. |
| **Confidence Engine** | 🔴 Planned | Auto-incrementing and auto-decrementing confidence levels based on run successes. |
| **Knowledge Graph** | 🔴 Planned | Relational index mapping of card dependencies (`DEPENDS_ON`, `PREVENTS`, `ENHANCES`). |

---

## 7. The Comprehensive 11-Phase Implementation Roadmap

To transition this framework to an fully automated operating knowledge ecosystem, we define the exact, production-ready specifications for all eleven phases. Each phase is mapped to its deployment validation gates and outcomes:

### Phase 1 — Inventory (Status: ✅ Complete)
*   **Objective:** Discover and map every existing conceptual card and file representation.
*   **Fields Covered:** Complete audit of `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, and workspace procedures (`checklists/`).
*   **Verification Gate:** Success is achieved when every operational document is correctly cataloged in our index without silent automated modifications.

### Phase 2 — Standardize (Status: ✅ Complete)
*   **Objective:** Define a unified, canonical schemas for all cards.
*   **Unified Model Schema:** Every card must conform to a standardized JSON schema containing unique UUID, type classification, schema version, status, confidence metrics, validation state, related/parent links, security classification, and evidence references.
*   **Verification Gate:** Automated unit tests validating model schemas against rigid JSON schemas.

### Phase 3 — Build the Engine (Status: 🔴 Next Milestone)
*   **Objective:** Construct the core `solomon_knowledge_cards` SQLite-backed storage and API layer.
*   **Requirements:**
    *   Robust SQLite table definitions supporting cards, metadata, and relations.
    *   Atomic transactional writes, tag indexing, and soft deprecation fields.
    *   No-destructive overwrite card history tables tracking sequential updates.
    *   Full JSONL export and recovery import routines.
*   **Verification Gate:** Complete unit test coverage for SQLite migrations, concurrency, backup integrity, and metadata queries.

### Phase 4 — Automatic Capture (Status: 🔴 Planned)
*   **Objective:** Automate draft generation from post-task outcomes.
*   **Process:** Background extraction pipelines converting `Worker Reports` and optional `SS3 Review Packets` into `DRAFT` or `PENDING_REVIEW` Knowledge Cards.
*   **Fields Extracted:** Attempted steps, success/failure context, error logs, root cause analysis, and evidence links.
*   **Verification Gate:** Proof that a completed mock worker report correctly yields a reviewable card in the `DRAFT` state.

### Phase 5 — Retrieval Before Execution (Status: 🔴 Planned)
*   **Objective:** Pre-populate worker systems with cumulative experience.
*   **API Query Interface:** Before task runs, a query (e.g., *"Find prior failures related to timeout errors"*) triggers standard BM25 and keyword filters.
*   **Payload Output:** Return highly-ranked, approved cards, including confidence, validation state, and links to relevant parent Procedure Cards.
*   **Verification Gate:** Pre-task prompt integration verified using context limits (e.g., token-budgeted packaging).

### Phase 6 — Reflection (Status: 🔴 Planned)
*   **Objective:** Continuous learning through log comparison.
*   **Process:** Evaluators compare expected task outcomes against actual timelines, resource expenditures, quality metrics, and unexpected discoveries.
*   **Verification Gate:** Reflection logs successfully generate candidate Success, Failure, and Repair card drafts.

### Phase 7 — Procedure Improvement (Status: 🔴 Planned)
*   **Objective:** Dynamic self-evolution under strict safety protocols.
*   **Process:** When multiple Knowledge Cards consistently optimize or update execution logs, candidate revisions to Procedure Cards are generated.
*   **Safety Gate:** Revisions never overwrite live files automatically; instead, they are pushed to a `REVIEW_PACKAGE` queue requiring human administrator verification.
*   **Verification Gate:** Successful test demonstrating rejection/approval promotion flows.

### Phase 8 — Skill Discovery (Status: 🔴 Planned)
*   **Objective:** Mapping structural boundaries and capability expansion.
*   **Process:** When a worker encounters an unresolvable error or unsupported task, a `MISSING_SKILL` card is generated. Research pipelines evaluate open-source alternatives, package options, and estimate development risk/effort.
*   **Verification Gate:** Report outlining recommended implementation pathways generated automatically when task requirements exceed current capability limits.

### Phase 9 — Knowledge Graph (Status: 🔴 Planned)
*   **Objective:** Semantic connection architecture.
*   **Edges:** Map explicit directed relationship edges between cards (e.g., `DEPENDS_ON`, `PREVENTS`, `ENHANCES`, `PROPOSES_UPDATE_TO`).
*   **Verification Gate:** Recursive graph queries successfully fetching all relevant associated cards up to N levels.

### Phase 10 — Metrics (Status: 🔴 Planned)
*   **Objective:** Telemetry and optimization dashboards.
*   **Metrics Tracked:** Total Cards Created, Reuse Rate, repeated failures saved, search speed/latency, and human oversight time saved.
*   **Verification Gate:** Telemetry reports rendered as JSON files (e.g., `growth_metrics.json`) periodically.

### Phase 11 — Passive Exponential Growth (Status: 🔴 Planned)
*   **Objective:** Idle-cycle system self-maintenance and alignment.
*   **Actions:** While idle, Solomon cleans duplicate cards, validates stale knowledge bases, runs background regression tests on updated procedures, and parses open-source releases.
*   **Safety Rule:** Under no circumstances are live production cards modified without human/governed approval.
*   **Verification Gate:** Verified background execution loops triggered gracefully during system downtime.
