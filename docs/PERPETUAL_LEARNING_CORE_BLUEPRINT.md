# Blueprint: The Domain-Neutral Perpetual Learning Core (PLC)

This document establishes the architectural blueprint, design principles, and guidelines for isolating the domain-neutral **Perpetual Learning Core (PLC)** from specialized cognitive adapters (such as Solomon's software development configuration).

---

## 1. Architectural Philosophy

The true value of Project Mnemosyne is not Solomon itself, but the underlying perpetual learning engine. By separating the core learning loop from specialized toolchains, personalities, and operational domains, we create a highly reusable architecture that can learn almost any field—software engineering, advanced manufacturing, medical research, or educational tutoring.

### Core Loop Lifecycle
```text
Raw Experience (Worker Reports, Documents, Chats, Logs)
                     ↓ Ingest (PLC Core)
Knowledge Extraction (Facts, Procedures, Warnings, Skills)
                     ↓ Validate & Govern (SS3 Review Gate)
Persistent Store (Mnemosyne Card Database)
                     ↓ Ranked Retrieval (FTS, Semantics)
Apply & Measure (LLM System Prompt / Execution)
                     ↓
Autonomous Self-Improvement Selection (Bottleneck Analysis)
```

---

## 2. Separation of Concerns: Core vs. Adapters

To preserve the reuse of this architecture, we strictly separate **Domain-Neutral Core Services** from **Specialized Application Adapters**.

### 2.1 The Perpetual Learning Core (PLC)
The PLC is the foundational system. It contains no domain-specific knowledge, tool specifications, or identity definitions.

- **Experience Intake:** Generic structured ingestion pipelines accepting system outcomes, conversation transcripts, task outcomes, or sensor data.
- **Knowledge Extraction:** NLP / parsing logic to extract cognitive cards (facts, procedures, pitfalls, and repair playbooks) from raw logs.
- **Evidence & Validation:** Historical provenance tracking (where did this card come from, what evidence exists, what is its confidence metric).
- **Memory Lifecycle Engine:** Code or database models handling state transitions (`DRAFT` -> `REVIEWED` -> `APPROVED` -> `ACTIVE` -> `DEPRECATED`), revision histories, merging, and soft deletions.
- **Hierarchical Access Retrieval:** Security and clearance level boundaries managing card selection based on runtime credentials.

### 2.2 Application Adapters
Adapters configure the core for a specific job, personality, and operational capability.

| Component | Solomon (Software Engineer) | Vulcan (Manufacturing AI) | Socrates (Tutor AI) |
|---|---|---|---|
| **Identity Profile** | Primary software capability coordinator | Factory line operations assistant | Empathetic educational assistant |
| **Ingress interface** | Custom GPT Action proxy (`7420`) | Factory telemetry queues / APIs | Interactive web chat / LMS |
| **Ingress Auth** | `SOLOMON_ACTIONS_API_KEY` | Machine certificate signature | Classroom auth token |
| **Active Tools** | `openhands_run`, `github_search_and_clone` | Modbus / PLC controller read/write | Assessment scoring, child-safety gates |
| **Knowledge Base** | Code repo files, Python/JS checklists | Machine manuals, defect logs, OSHA rules | Curriculum maps, student capability models |

---

## 3. Critical Design Rules

From this point forward, all developers and agentic sub-workers must adhere to these design rules:

1. **Domain-Neutral Core Namespaces:** Under no circumstances should domain-specific names (such as `Solomon`, `OpenHands`, `Codex Carl`, or `scrapers`) be hardcoded inside `solomon_knowledge_cards/runtime.py`, `models.py`, or generic SQL schemas.
2. **Encapsulated Ingestion Schemas:** Ingestion structures (e.g. Worker Reports) must use generic keys like `attempted`, `succeeded`, `failed`, and `evidence` rather than coding-specific keys like `changed_files` or `test_results`. In coding environments, those specific keys belong inside a nested `metadata` dictionary.
3. **Externalized Identities:** Prompts regarding the AI's identity, mission, or specific workspace parameters belong in external configurations or system-prompt templates. The PLC core simply retrieves relevant cards and formats a generic background context.
4. **Adapter Isolation:** All tool wrappers, API endpoints, and specific proxy servers belong in separate integration modules or deployment wrappers (e.g., `app.py`, `solomon-proxy.js`, or custom tool directories) rather than the `solomon_knowledge_cards` package.
