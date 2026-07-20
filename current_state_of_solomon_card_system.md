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

## 7. Next Milestone: The Knowledge Card Engine

To close the loop and transition from document-driven rules to an active self-learning system, the immediate recommended engineering objective is the **Knowledge Card Engine**.

The engine will automate the loop by converting:
- Worker execution reports
- Post-task review packets
- Execution errors, failures, and manual hotfixes

into standardized, indexed **Knowledge Cards**. These cards will act as dynamic system proposals that automatically patch or update parent **Procedure Cards** under automated safety and human-in-the-loop governance. This will finalize Solomon's evolution into a robust, self-improving operating knowledge ecosystem.

---

## 8. Blueprint for the Perpetual Learning Core (PLC)

To guide the long-term evolution of Solomon, we integrate the **Perpetual Learning Core (PLC)** vision blueprint. This is the architectural north star designed to make Solomon a self-improving cognitive system.

### A. Executive Vision
Solomon is a **Perpetual Learning Machine**. Specialty domains (Software Engineering, Research, Analysis, Medicine, Robotics) are dynamic skills that can be acquired. The core cognitive learning engine remains entirely domain-independent.

### B. The Ten Cognitive Layers

#### Layer 1: Experience Engine
Captures everything Solomon experiences in real time, including conversations, code execution logs, worker reports, literature search, human interactions, and failures/successes.

#### Layer 2: Knowledge Distillation Engine
Converts raw experiences into structured, semantic cards (Fact, Concept, Procedure, Lesson Learned, Warning, Failure, Best Practice, Decision, Relationship).

#### Layer 3: Memory Card System
Requires that every memory unit contain explicit audit markers (UUID, Confidence, Evidence, Source, Author, Version, Dependencies, and SS3 Validation status).

#### Layer 4: Knowledge Graph
Establishes directed semantic connections among cards (`Requires`, `Supports`, `Contradicts`, `Improves`, `Replaces`, `DerivedFrom`).

#### Layer 5: Capability Graph
Tracks specialized capabilities and their prerequisites, tools, reliability metrics, and performance limits.

#### Layer 6: Retrieval Engine
Pre-populates working contexts with relevant procedures, similar failures, and successfully applied repairs before reasoning begins.

#### Layer 7: Reasoning Engine
Governs planning, decision-making, task decomposition, and risk analysis. Reasoning never directly edits long-term memory; it proposes updates.

#### Layer 8: Builder Engine
Generates assets (Code, SOPs, documentation, tests, scripts) to carry out actions.

#### Layer 9: Reviewer Engine (SS3)
An independent verification gate assessing correctness, reproducibility, and safety before promoting draft memories.

#### Layer 10: Evolution Engine
The meta-learning component. After each task, it assesses what made the task difficult, what skills were missing, and dynamically schedules card generation or skill acquisitions.

### C. Learning Hierarchy
1.  **Level 1:** Learn Facts.
2.  **Level 2:** Learn Procedures.
3.  **Level 3:** Learn Strategies.
4.  **Level 4:** Learn Skills.
5.  **Level 5:** Learn How To Learn Faster.
6.  **Level 6:** Improve the Learning System Itself (The Ultimate Goal).

### D. Three-Box Governance
-   **SS1 (Production Brain):** Stable operational runtimes only.
-   **SS2 (Experimental Lab):** Learning, building, testing, and drafting new cards.
-   **SS3 (Independent Reviewer):** Security checks, code audits, and promotion approval. No automated edit reaches SS1 without SS3 approval.
