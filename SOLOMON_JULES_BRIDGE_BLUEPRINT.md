# Solomon–Jules Bridge Architecture Blueprint

## Overview
The Solomon-Jules connection avoids relying on browser automation for core tasks, recognizing the instability of web UI changes. Instead, it relies on a strict, robust hierarchy:
1. **Jules REST API** (Primary)
2. **Jules CLI** (Secondary / Operator Interface)
3. **GitHub** (Workspace and artifact storage)
4. **Browser automation** (Emergency fallback only)

## Three-Box Deployment Strategy
This bridge enforces strict boundaries across three conceptual environments:

*   **SS1 — Production:** Solomon API, memory, task scheduling. NO experimental browsing or direct Jules patches allowed.
*   **SS2 — Development and Worker:** Houses the Jules API adapter, CLI, GitHub interactions, and a disposable Playwright browser profile. This is where patches are pulled and built.
*   **SS3 — Validation:** A clean checkout space for tests, security scanning, regression testing, and generating the final approval packet for a human.

## Core Component: `solomon_jules_bridge.py`
The bridge defines the following internal API for Solomon:
- `create_jules_task()`: Initiates a task securely via the API (using `X-Goog-Api-Key`).
- `list_jules_tasks()`: Polls active sessions.
- `read_jules_session()`: Checks the status of a specific task.
- `send_jules_message()`: Sends follow-up instructions.
- `cancel_jules_task()`: Aborts a run.
- `retrieve_jules_patch()`: Pulls the resulting code into SS2.
- `validate_jules_output()`: Triggers tests in SS3.
- `request_human_approval()`: Flags the validated patch for a human click.

## Example Task Record
```json
{
  "task_id": "SJ-2026-0042",
  "repository": "project-solomon",
  "branch": "development",
  "objective": "Implement relational memory-card linking",
  "source": "solomon",
  "execution_target": "jules",
  "environment": "SS2",
  "risk": "medium",
  "requires_plan_approval": true,
  "requires_merge_approval": true,
  "status": "submitted"
}
```

## Security & Access Boundaries
Solomon **cannot** independently:
* Expose API keys.
* Connect private repositories.
* Merge directly to SS1 without SS3/Human checks.
* Alter billing or repository protections.

## The Browser Extension's True Role
The Solomon Browser Extension acts as a *shared browsing companion*. It provides visibility into what Solomon sees, allows humans to refine prompts before they are sent to the Jules API, and serves as the UI for the final `request_human_approval()` click. It is **not** the transport layer for Jules tasks.