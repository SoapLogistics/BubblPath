# Capability Registry

*Last Synced: 2026-07-20 09:47:32 UTC*

## New Capability Proposals

### CP-001: Flask API Security Gate (High Leverage)
*   **Problem:** Flask endpoint `/chat` is exposed to public routing without auth checks, draining OpenAI credits if abused.
*   **Impact:** Severity 1 Security Risk.
*   **Dependencies:** None.
*   **Estimated Value:** Protects platform resources, ensures controlled access.
*   **Security Review:** Restricts requests to those presenting valid Bearer headers.
*   **Governance Review:** Human operator configures security tokens in `.env`.

### CP-002: Programmatic Autonomous Cycle Runner (Ultimate Growth Catalyst)
*   **Problem:** Scheduled tasks inside `HEARTBEAT.md` (baseline health checks, hourly syncs) are written in markdown, but cannot run themselves.
*   **Impact:** Solomon remains passive, relying on manual operator invocations.
*   **Dependencies:** Capability CP-001, Python scheduler module.
*   **Suggested Open Source Projects:** APScheduler, Celery.
*   **Acceptance Criteria:** A background thread executes hourly, successfully synchronizing workspace status to Git.
