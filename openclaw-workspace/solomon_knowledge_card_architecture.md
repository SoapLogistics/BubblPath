# Solomon Knowledge Card Architecture (SOSS) & Evolution Roadmap

- **Document ID:** SOSS-ARCH-01
- **Focus Area:** Cognitive Memory Evolution, Knowledge Graphs, and Dynamic Procedure Promotion
- **Author:** Jules, Systems Architect
- **Status:** APPROVED / READY FOR IMPLEMENTATION

---

## 1. Executive Summary

This architecture document outlines the evolution path of **Solomon’s** brain from its current **Lightweight OpenClaw Workspace Memory System** to the **Solomon Knowledge Card Architecture (Solomon Operating System Sub-structure - SOSS)**.

While the current system provides an excellent, low-latency, markdown-based operational memory, it lacks structured data-types, graph-based querying, and automated self-synthesis. SOSS bridges this gap by introducing **Typed Knowledge Cards**, directed semantic relationships, confidence/reliability tracking, and a dynamic **Procedure Promotion Engine**. This architecture enables Solomon to autonomously absorb open-source code, document failures, adjust operational trust, and scale passive exponential growth with zero human oversight.

---

## 2. Current State: OpenClaw Workspace Memory Inventory

The existing workspace memory located at `/srv/storage/toshiba/BubblePath/openclaw-workspace/` acts as the bootstrap memory. Below is the inventory and analysis of these files:

### 2.1 Core Identity and Soul Files
- **`IDENTITY.md`:** Establishes the agent profile for **Solomon**, defining its static role as an Autonomous Omni-Agent, its mission of passive exponential growth, and its deep-ocean weaver avatar.
- **`SOUL.md`:** Governs persona, tone (concise, direct, expert), and core values (traceability, security, self-evolution). It defines the *Continuity Philosophy* for preserving context across 24/7 asynchronous turns using handover notes.
- **`USER.md`:** Outlines the human operator's preferences and defines Level 1 (Self-Healing) and Level 2 (User Escalation) rules.

### 2.2 Operational and Environmental Context Files
- **`TOOLS.md`:** Registers local tools (file system, bash) and sub-agent integration definitions for OpenHands (agentic coding) and CrewAI (multi-agent orchestration), along with dynamic MCP tool registration parameters.
- **`MEMORY.md`:** Governs the "Iron Laws of Memory Management" (e.g., no raw secret logging, private-only loading) and tracks known environment ports and network patterns.
- **`HEARTBEAT.md`:** A compact execution checklist (<50 lines) that runs on 10-minute triggers to audit system health, resources, and sync git state.

### 2.3 Operational checklists/ (Procedure Cards)
- **`checklists/autonomous_cycle.md` (PC-AC-01):** The master 24/7 loop protocol detailing heartbeat validation, state synchronization/resumption, and background execution.
- **`checklists/openhands_integration.md` (PC-OH-01):** Steps for branch creation, running OpenHands Docker sessions, compiling code, and cleanup.
- **`checklists/crewai_integration.md` (PC-CA-01):** Guidelines for validating CrewAI YAML configs, tracking resources, and parsing structured JSON outputs.
- **`checklists/solomon_code_absorption.md` (PC-SO-01):** The core process for discovering open-source repositories, parsing forums ("gossip pages"), checking licenses, and compiling wrappers.
- **`checklists/passive_exponential_growth.md` (PC-SO-02):** The compounding growth protocol covering opportunity audits, micro-product deployment, and marketing outreach automation.

---

## 3. Target State: SOSS Knowledge Card Architecture

The Solomon Knowledge Card Architecture transforms flat markdown files into a queryable, semantic, and relational database graph.

```
                          ┌────────────────────────┐
                          │     SOSS Core Graph    │
                          └───────────┬────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
   [Knowledge Cards]            [Relationships]            [Metadata & Telemetry]
   - LessonCard                 - mitigates                - Confidence Metrics
   - FailureCard                - derived_from             - Success Ratios
   - SkillCard                  - requires_skill           - Verification State
   - DecisionCard               - triggered_by             - Dynamic Query Retrieval
   - ArchitectureCard
```

### 3.1 Typed Knowledge Cards

Every unit of memory in SOSS is represented as a structured node called a **Knowledge Card**. There are 5 specialized card types:

1. **`LessonCard` (Learnings & Patterns):**
   - *Contents:* Observations, code performance results, forum-derived tips, and generalized solutions.
   - *Schema:* `{ card_id, title, context, summary, open_source_reference, verified_date }`
2. **`FailureCard` (Errors & Recovery):**
   - *Contents:* Exact exit codes, stack traces, identified root causes, and successful remediation steps.
   - *Schema:* `{ card_id, error_signature, stack_trace, root_cause, mitigation_action_id }`
3. **`SkillCard` (Dynamic Capabilities):**
   - *Contents:* Python/Node CLI commands, package parameters, and dynamic Model Context Protocol (MCP) server endpoints.
   - *Schema:* `{ card_id, tool_name, command_template, mcp_schema, permission_boundary }`
4. **`DecisionCard` (Rationale & Trade-Offs):**
   - *Contents:* Why a specific open-source library was chosen over another, architectural compromises, and resource allocations.
   - *Schema:* `{ card_id, decision_topic, alternatives_evaluated, selected_option, rationale_details }`
5. **`ArchitectureCard` (Topology & State):**
   - *Contents:* Docker network bridges, sub-agent dependency trees, port maps, and state-machine transitions.
   - *Schema:* `{ card_id, layer_name, network_configuration, dependency_list, state_transitions }`

---

## 4. Directed Semantic Relationships & Connections

Knowledge Cards are interconnected by explicit, directed relationships to form an operational knowledge web:

- **`mitigates`:** Connected from a `LessonCard` or `SkillCard` to a `FailureCard`. Allows Solomon to instantly lookup how a past crash was solved.
- **`derived_from`:** Links an `ArchitectureCard` or `DecisionCard` to the web gossip thread or GitHub repository from which it was absorbed.
- **`requires_skill`:** Links a task or `DecisionCard` to the necessary `SkillCard` needed for execution.
- **`triggered_by`:** Connects a `FailureCard` to the specific `ArchitectureCard` state or tool invocation that caused it.

---

## 5. Confidence, Reliability, & Retrieval Mechanics

To prevent hallucinated tools and stale configurations from degrading execution loops, SOSS implements an active reliability layer:

### 5.1 Telemetry Metrics
- **Success Ratio ($S$):** $S = \frac{\text{Successful Executions}}{\text{Total Executions}}$.
- **Confidence Score ($C$):** A real-time float $[0.0, 1.0]$ representing overall tool/process trust.
  - $C$ is increased by verification checks (read-back validations) and decayed dynamically over idle time ($t$):
    $$C_{t} = C_{0} \times e^{-\lambda t}$$
    Where $\lambda$ is the operational decay coefficient.
- **Verification State:** `UNVERIFIED` (newly absorbed), `VERIFIED_SANDBOX` (tested in isolation), or `VERIFIED_PRODUCTION` (stable across multiple heartbeat cycles).

### 5.2 Retrieval & Querying Mechanics
Before executing a task or compiling code, Solomon queries the SOSS graph using hybrid search:
1. **Vector Embedding Search:** Generates a semantic vector of the current task and queries a local vector store (e.g., Chromadb, pgvector) to fetch relevant `LessonCards` and `FailureCards`.
2. **Graph Traversal Query:** Follows directed links (e.g., finding the `SkillCard` that `mitigates` the retrieved `FailureCard`).
3. **Prompt Compilation:** Inject only the high-confidence cards into Solomon's system prompt, keeping token usage under 2,000 tokens while ensuring high contextual relevance.

---

## 6. Dynamic Procedure Promotion Engine

The SOSS **Procedure Promotion Engine** automates the transition of ad-hoc learnings into hardened operational procedures:

```
┌─────────────────┐     (Matches Error Pattern)     ┌─────────────────┐
│   FailureCard   ├────────────────────────────────>│    LessonCard   │
└─────────────────┘                                 └────────┬────────┘
                                                             │ (Success Rate > 90%
                                                             │  Over 10 Cycles)
                                                             ▼
                                                    ┌─────────────────┐
                                                    │  Procedure Card │
                                                    │  (Checklists)   │
                                                    └─────────────────┘
```

1. **Aggregation:** As Solomon resolves issues, it creates `FailureCards` linked to successful `LessonCards` and `SkillCards`.
2. **Evaluation:** Every 24 hours, the engine scans the graph for recurring combinations where a specific remediation shows a **Success Ratio > 90% over at least 10 executions**.
3. **Synthesis:** The engine triggers a CrewAI copywriting session to merge the relevant cards into a new, highly structured, markdown-compatible **Procedure Card** (Checklist format) inside the `checklists/` directory.
4. **Bootstrapping:** The master `AGENTS.md` is updated dynamically to register the new Procedure Card, making it immediately available for the 24/7 autonomous loop.

---

## 7. Concrete Evolution Path & Migration Steps

To transition smoothly from Markdown workspace files to the full SOSS database graph:

### Phase 1: Database Initialization & Schema Deployment
- Spin up an embedded SQLite or PostgreSQL instance within `/srv/storage/toshiba/BubblePath/`.
- Run the SOSS database migrations to create tables for Nodes (Knowledge Cards) and Edges (Directed Relationships).

### Phase 2: Markdown Bootstrap Parser (The SOSS Ingestion Script)
- Execute a Python script that reads the existing OpenClaw workspace files and programmatically seeds the SOSS database:
  - Parse `MEMORY.md` and extract environment port records to seed the first `ArchitectureCard`.
  - Parse `TOOLS.md` to seed `SkillCards` for OpenHands and CrewAI.
  - Parse `checklists/*.md` to populate the initial Procedure index.
- *Ingestion Pseudo-Code Example:*
  ```python
  def ingest_markdown_to_soss(file_path, card_type):
      content = read_markdown(file_path)
      # Extract structural sections using regex
      card_id = extract_card_id(content)
      db.insert_node(card_id, card_type, content)
      print(f"Ingested {card_id} as {card_type}")
  ```

### Phase 3: Runtime API Middleware Integration
- Modify Solomon's central gateway (`app.py`) to hook into SOSS:
  - **Pre-execution hook:** Query SOSS graph vector embeddings to inject custom knowledge.
  - **Post-execution hook:** Capture execution status, update confidence scores, write any new `FailureCard` or `LessonCard` directly to database tables.

### Phase 4: Full Autonomy & Compounding Growth
- Enable the scheduled Procedure Promotion Engine in the heartbeat loop.
- Allow Solomon to dynamically write its own SQLite/PostgreSQL schema updates and scale the SOSS graph endlessly.
