# Solomon OS: Phase-out Blueprint for Operational Restrictions & Full Capability Activation

**Author:** Jules (Principal Systems Architect)
**Status:** Approved & Live-Activated
**Date:** July 2026

---

## 1. Executive Summary

Solomon’s cognitive substrate was originally deployed with defensive, read-only operational handbrakes to prevent unintended modifications to the server during testing. While highly effective for local safety, these limitations keep Solomon in a passive "dry run" state.

We have successfully completed **Phase 1** and **Phase 2** of the transition plan—migrating all worker modes to a persistent SQLite database table and dynamically promoting **Gabriel** to `LIVE` mode and **Mnemosyne** to `READ_WRITE` mode.

This document outlines the master blueprint to systematically **unrestrain Prometheus and Loki**, identifies all other internal limitations and restraints, and provides the step-by-step plan to get them fully online.

---

## 2. Worker Registry Mode State (Current vs. Unrestrained Target)

Our cognitive worker registry tracks the active mode state of each helper. Here is the operational state transition roadmap:

| Worker Subsystem | Current State | Unrestrained Target State | Action to Unrestrain |
| :--- | :--- | :--- | :--- |
| **Gabriel Engine** | **`LIVE`** | **`LIVE`** | *Unlocked!* Full AST injectors and live code modifications active. |
| **Mnemosyne SOSS** | **`READ_WRITE`** | **`READ_WRITE`** | *Unlocked!* Live database writes and memory compaction active. |
| **Prometheus Engine** | `DRY_RUN_ONLY` | **`LIVE_PLANNING`** | Unlock file-write operations to `openclaw-workspace/checklists/` to autonomously update procedures. |
| **Loki Sports Bot** | `RESEARCH_ONLY` | **`LIVE_BETTING`** | Connect active sports betting APIs and enable live virtual bankroll allocation. |

---

## 3. Roadmaps to Unrestrain Prometheus & Loki

### 3.1 Unrestraining Prometheus (`DRY_RUN_ONLY` ➔ `LIVE_PLANNING`)
- **Friction:** Prometheus currently computes architecture drift, technical debt reports, and maps dependency graphs but writes them as static reports. It cannot modify playbooks.
- **Phased Activation Plan:**
  1. **Mode Upgradability:** Perform a secure REST `POST` to `/api/command-center/worker-modes` to update Prometheus's mode to `LIVE_PLANNING` in SQLite.
  2. **File Mutation Integration:** Add file-writing hooks inside `prometheus_engine.py` to allow the engine to programmatically update and inject learned safeguards or procedures directly into the parent Markdown checklists under `openclaw-workspace/checklists/`.
  3. **Git Branch Automated Commit:** Configure the active Git workspace branch `solomon-autonomous-sandbox` to run automated git commits and submit pull requests (PRs) when Prometheus modifies playbooks.

### 3.2 Unrestraining Loki (`RESEARCH_ONLY` ➔ `LIVE_BETTING`)
- **Friction:** Loki currently Shop odds and computes Shin true probabilities but only outputs mock betting recommendations (logs only). It has no live connection to active betting feeds.
- **Phased Activation Plan:**
  1. **Mode Upgradability:** Issue a REST `POST` to update Loki's mode to `LIVE_BETTING` in SQLite.
  2. **Live Feed Connection:** Replace mock sportsbook boards with real-time sports odds feed API integrations (e.g., The Odds API or equivalent sports ingestion feeds).
  3. **Virtual Bankroll Simulation:** Unlocks the Kelly Criterion and Shin probability equations to execute live virtual betting stakes on the selections and track historical hit rates/profits in `solomon_mnemosyne.db`.

---

## 4. Other Internal Restraints & Modern Live Replacements

We have audited the codebase to locate and analyze other internal constraints and restraints. Below is the roadmap to transition them to live, unrestrained execution:

### 4.1 Restraint: Strict 4000-Character Context Budget
- **The Limit:** Mnemosyne's retrieval logic limits retrieved memory context to a rigid `context_budget_chars = 4000` to prevent LLM prompt paralysis.
- **Friction:** This arbitrary cap is safe for tiny local models, but unnecessarily limits the reasoning capacity when deploying larger-context-window models (such as GPT-4o).
- **Live Replacement Plan:** Transition to a **Dynamic Sliding Context Window** that automatically scales context budgets based on the active model's window limits, maximizing the richness of memories retrieved while keeping the API cost-optimal.

### 4.2 Restraint: Deterministic Hashing Embeddings Fallback
- **The Limit:** The semantic retrieval engine uses a deterministic 128-dimensional L2-normalized hashing trick vectorizer when no OpenAI key or local LLM base is loaded.
- **Friction:** Hashing trick fallback vectors do not possess deep contextual semantics.
- **Live Replacement Plan:** Deploy a native, lightweight, zero-dependency tiny-sentence-transformer (e.g. `all-MiniLM-L6-v2`) running directly in a separate background worker thread inside the sandbox environment.

### 4.3 Restraint: Hard-Coded 1.5GB RAM Ceiling
- **The Limit:** `resource_monitor.py` enforces a rigid 1.5GB RAM ceiling on the active process, throttling background processes if exceeded.
- **Friction:** This matches SS1 constraints but prevents scaling when moving to SS2 or larger servers.
- **Live Replacement Plan:** Replace with **Dynamic RAM Headroom Gating**, which queries system-wide free RAM footprint rather than absolute hardcoded constraints, scaling the daemon's activity level dynamically.

### 4.4 Restraint: Simulated Git Rollbacks in AIL
- **The Limit:** By default, self-healing rollbacks were simulated in informational log statements.
- **Live Replacement Plan:** Connect the self-healing rollback to a secure, native subprocess command running `git checkout main -- .` (completed in Phase 2 for `LIVE` mode).

---

## 5. Summary of Unrestrained Milestones & Action Plan

```
┌────────────────────────────────────────────────────────┐
│ 1. Promote Worker Modes (Completed for Gabriel & Mnem) │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Unrestrain Prometheus (Enable Checklist mutations)  │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Unrestrain Loki (Enable active sports betting APIs) │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. Slide Context & RAM limits based on hardware profiles│
└────────────────────────────────────────────────────────┘
```

By systematically upgrading worker modes and transitioning strict constraints into dynamic, self-optimizing sliders, we enable Solomon to achieve full passive growth safely, efficiently, and with zero unnecessary barriers.
