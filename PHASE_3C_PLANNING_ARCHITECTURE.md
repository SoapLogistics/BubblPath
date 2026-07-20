# Solomon Cognitive OS: Planning Layer Architecture (Phase 3C)

This document details the architectural layout, core components, and operational flow diagrams of Solomon's **Planning Layer** (Phase 3C). This layer bridges the gap between historical Knowledge and active execution.

---

## 1. Component Overview & Responsibilities

The Planning Layer is structured as a dedicated submodule under `solomon_knowledge_cards/planner/`.

```
                         ┌─────────────────────────────┐
                         │    Task / Objective Ingest  │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │       DynamicPlanner        │
                         │  - Queries Mnemosyne Cards  │
                         │  - Identifies prior failures│
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   Pre-emptive Safeguards    │
                         │  - Injects SG-steps into    │
                         │    the drafted TaskPlan     │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │        ToolArbiter          │
                         │  - Arbitrates tool configs  │
                         │    (e.g., port 3000->3001)  │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │    Safe Task Execution      │
                         └─────────────────────────────┘
```

### A. TaskPlan Model (`planner/models.py`)
- Standardizes the structured representation of autonomous step sequences.
- Tracks plan-level metadata: `plan_id`, `objective`, `steps`, `retrieved_memory_card_ids`, `injected_safeguards`, and execution `status` (`DRAFT`, `APPROVED`, `EXECUTED`, `FAILED`).

### B. Dynamic Planner Engine (`planner/engine.py`)
- Receives execution objectives and queries the Mnemosyne memory store for relevant past experiences.
- Translates retrieved Failure and Repair memories into concrete pre-emptive steps that are injected *before* standard actions.

### C. Tool Selection Arbiter (`planner/arbiter.py`)
- Analyzes tool configs against active playbooks to dynamically override runtime parameters.
- For example, if port busy constraints are known, it pre-emptively modifies connection config ports from `3000` to `3001` to guarantee run success.

---

## 2. Dynamic Safeguard Ingestion Flow

1. **Step Ingest:** An objective (e.g., "Deploy OpenHands container") is sent to `/planner/draft`.
2. **Retrieve:** The planner executes a semantic hybrid query against Mnemosyne.
3. **Filter:** Discovers an approved Repair Card `RC-PORT-REWRITE` detailing port busy conflicts on port 3000.
4. **Formulate & Inject:**
   - Injects a pre-emptive safeguard step: `PRE-EMPTIVE SAFEGUARD: Kill process on port 3000`.
   - Appends standard baseline actions after the safeguard.
5. **Arbitrate:** When executing, the `ToolArbiter` overrides target ports to `3001`.
6. **Execution Success:** The worker loop runs cleanly without resource conflicts, completing the self-healing loop.
