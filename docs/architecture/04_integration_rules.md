# Integration Rules

This document outlines the strict protocols governing system interoperability, promotion pipelines, and the execution of high-risk operations within the Solomon architecture.

## 1. The ThreeBoxQueue Promotion Path
All capabilities, knowledge, and code modifications must follow the SS2 -> SS3 -> SS1 pipeline managed by `solomon_three_box_role_contract.py`.

*   **SS2 (Learning Laboratory):** Where Gabriel performs sandbox evaluations, clean-room constructions, and Crucible testing. Dynamic code loading and AST injection are permitted *only* here.
*   **SS3 (Gatekeeper Review):** Independently reruns SS2 outputs. Evaluates reproducibility, security bounds, and regression risks. Output must be signed for promotion.
*   **SS1 (Production Runbook):** The stable runtime. Only approved, static artifacts from SS3 may run here.

## 2. Governance Approval Lane
*   **Rule:** High-risk actions on SS1 (e.g., `git_push`, `sudo`, `ss1_mutation`) are strictly blocked by default.
*   **Enforcement:** Operations are intercepted by `solomon_governance_approval_packet.py`. They cannot proceed without explicit `mark_approval` and `ss3_review` contexts supplied in the payload.
*   **Tracking:** State transitions (pending -> approved) are deterministically logged in `governance_log.bin`.

## 3. Sandboxing & Isolation
*   **Gabriel Quarantine:** The Gabriel engine operates strictly within SS2. It must never execute dynamic code on the main SS1 gateway process.
*   **Path Traversal Protection:** Dynamic loaders (e.g., `gabriel_engine/core/dynamic_loader.py`) and AST injectors must sanitize inputs against directory traversal (restricting writes strictly to temporary/workspace boundaries) and use alphanumeric name enforcement.

## 4. Initialization and Startup Routines
*   **Route Registration:** In the Unified Flask Gateway (`app.py`), all API routes must be fully registered before the blocking `app.run()` loop initiates.
*   **Daemon Safety:** Background Resident Daemons (e.g., Jules, Guardian) must utilize threading locks and initialization flags (e.g., `_residents_started = True`) to prevent duplicate instantiation across multi-worker server environments.
*   **Lazy Initialization:** Background managers requiring configuration (like `NashSwarmManager` checking `TESTING` flags) must be initialized lazily via getter functions, not globally at module load time.
