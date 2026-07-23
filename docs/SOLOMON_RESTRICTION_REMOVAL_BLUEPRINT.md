# Solomon OS: Phase-out Blueprint for Operational Restrictions

**Author:** Jules (Principal Systems Architect)
**Status:** Approved
**Date:** July 2026

---

## 1. Executive Summary

Solomon’s cognitive substrate was originally deployed with defensive, read-only operational handbrakes to prevent unintended modifications to the server during testing. While highly effective for local safety, these limitations keep Solomon in a passive "dry run" state.

This document catalogs every active operational limitation and outlines a rigorous **3-Phase Transition Plan** to systematically replace mock and read-only behaviors with live, database-backed read-write agentic actions, while preserving critical security, clearance, and resource constraints.

---

## 2. Catalog of Active Operational Restrictions

Through a thorough audit of the codebase, we have cataloged the following restrictions:

### 2.1 UI/Worker Level Restrictions
- **Gabriel (COMMAND_CENTER_RELAY):** Locked in `READ_ONLY` mode. Restricts Gabriel from writing physical AST modifications or dynamic loader capabilities to disk.
- **Mnemosyne (MEMORY_CONTEXT):** Locked in `READ_ONLY` mode. Prevents persistent, dynamic card clean-ups or runtime database compaction operations outside manual invocations.
- **Prometheus (BUILD_PLANNER):** Locked in `DRY_RUN_ONLY` mode. Restricts Prometheus from committing automated checklist proposals or editing `openclaw-workspace/checklists/` directly.
- **Loki (SPORTS_RESEARCH_MODEL):** Locked in `RESEARCH_ONLY` mode. Restricts Loki from allocating virtual bet stakes or feeding real betting/odds APIs.

### 2.2 System-Level Execution Restrictions
- **Mock Planner Fallback:** If `OPENAI_API_KEY` or `SOLOMON_LLM_API_BASE` is absent or fails, `/api/command-center/solomon-chat` returns a static fallback string: `"Hello, I am Solomon. I processed your request in mock planner mode."`
- **AIL Mock Discovery:** In `AutonomousImprovementLoop.run_discovery_and_absorption()`, candidate packages are hardcoded as a static `"Date Utility Helper"` python dictionary instead of querying PyPI or git.
- **AIL Simulated Rollback:** In `AutonomousImprovementLoop.trigger_abort_and_revert()`, the rollback action is printed as an informational log: `git checkout main -- .` rather than physically running Unix shell commands.

---

## 3. Phased Restriction Phase-out Plan

To safely transition Solomon into a fully operational live arsenal, we categorize the next initiatives into three core phases:

```
┌───────────────────────────────────────┐
│ PHASE 1: Persistent Mode Gating       │ (Dynamic database state, REST API toggle)
└───────────────────┬───────────────────┘
                    ▼
┌───────────────────────────────────────┐
│ PHASE 2: Hot-Swap Sub-Engine Bypasses  │ (Real git rollback, live API fallback)
└───────────────────┬───────────────────┘
                    ▼
┌───────────────────────────────────────┐
│ PHASE 3: Outer-Loop Integrations       │ (Docker execution SDK, MCP package pull)
└───────────────────────────────────────┘
```

### Phase 1: Database-Backed Active Worker State Persistence & REST Gating
- **Objective:** Move worker status from static/mock states to a persistent SQLite database table (`worker_modes`) in `solomon_mnemosyne.db` and expose REST API controls.
- **Actions:**
  1. Add a `worker_modes` schema inside the database backend.
  2. Register initial states (seeding `READ_ONLY`, `READ_ONLY`, `DRY_RUN_ONLY`, `RESEARCH_ONLY`).
  3. Expose `GET /api/command-center/worker-modes` and `POST /api/command-center/worker-modes` in `app.py` and proxy `solomon-proxy.js`.
- **Status:** **Ready for Immediate Implementation.**

### Phase 2: Hot-Swap Live-Execution Bypasses in All Sub-Engines
- **Objective:** Hook the sub-engines directly to the `worker_modes` states to execute live tasks instead of fallbacks when set to `LIVE` or `READ_WRITE`.
- **Actions:**
  1. Connect `AutonomousImprovementLoop`'s rollback method to execute real git commands (`git reset --hard`) when Gabriel/AIL are in `LIVE` mode.
  2. Implement live checklist updates inside the Prometheus planner when in `LIVE_PLANNING` or `READ_WRITE` mode.
  3. Swap mock-planner chat responses for real execution routing if configured.
- **Status:** **Ready for Immediate Implementation.**

### Phase 3: Active Outer-Loop Tool Integration & Sandboxing
- **Objective:** Connect Solomon's tools directly to the live environment using secure isolation lanes.
- **Actions:**
  1. Integrate the Docker SDK inside the AIL daemon to run test suites in ephemeral container sandboxes.
  2. Bind true Model Context Protocol (MCP) servers to pull package candidates dynamically.
- **Status:** **Planned for Future Deployment.**

---

## 4. Retained Critical Guardrails

To prevent system crashes under extreme conditions, we **MUST** retain the following security and platform limits:
1. **Resource Monitoring Cap (1.5GB RAM):** Hard memory checks via `resource_monitor.py` remain active to prevent out-of-memory (OOM) crashes on SS1.
2. **Directory Traversal Path Guards:** target paths must be strictly checked using `os.path.abspath` inside `/app` or `/home/jules`.
3. **Timing-Safe Token Authentication:** Protected API endpoints will continue to enforce timing-safe header validation.
4. **Hierarchical Security Clearance Gating:** Card filtering will strictly respect `PUBLIC` $\rightarrow$ `INTERNAL` $\rightarrow$ `RESTRICTED` security clearances.
