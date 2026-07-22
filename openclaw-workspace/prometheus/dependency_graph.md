# Dependency Graph

*Last Synced: 2026-07-20 09:47:32 UTC*

## System Interdependency Matrix

This matrix maps dependencies and verifies connection health.

| Origin Subsystem | Destination Subsystem | Connection Protocol | Dependency Type | Status |
| :--- | :--- | :--- | :--- | :--- |
| Flask App (`app.py`) | External LLM Gateway | HTTP POST API | Hard Runtime Dependency | **Connected (Unsecured)** |
| Prometheus Engine | Workspace Files (`checklists/`) | Local File Read | Hard Static dependency | **Connected (Functional)** |
| OpenHands Worker | Host Docker Daemon | Local UNIX Socket | Structural Sandbox Dependency | **Theoretical (Disconnected)** |
| CrewAI Framework | OpenAI Endpoint | API Token Request | External Compute Dependency | **Theoretical (Disconnected)** |
| Knowledge Card Engine | SS3 Memory Card Registry | SQLite/JSON storage | Hard Cognitive Dependency | *Under Active Dev* |

## Connection Protocol Rules
- **Direct Runtime:** Hard system crashes on interruption.
- **Asynchronous Queue:** Message-based retry resilience on network drop.
- **File System:** Isolated write operations inside user sandboxes.
