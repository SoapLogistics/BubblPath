# NEXT SUGGESTED TASKS
**Proposed Milestones for System Security, Hardening, and Scalable Autonomy (Phase 4)**

To move from an **"implemented baseline"** codebase to a fully **"hardened and autonomously scaling"** system, the following tasks are suggested:

## 1. API Bearer Token Authorization
- **Task:** Implement simple but robust Bearer token verification on all Flask endpoints (`/chat`, `/worker-report`, `/review`, `/cards`) to prevent unauthorized scraping of the LLM context or OpenAI API key drainage.

## 2. Global Try-Except Error Handling in API
- **Task:** Fortify `app.py` against OpenAI API failures or invalid database states by implementing strict `try-except` wrappers that safely log failures and return standard HTTP 500 JSON responses instead of crashing the worker.

## 3. Pin Dependencies in `requirements.txt`
- **Task:** Update `requirements.txt` from floating constraints to pinned, exact version numbers (e.g. `flask==3.1.3`) to guarantee identical environments across SS1, SS2, and SS3 testing and production deployment.

## 4. Task Queue API Endpoints
- **Task:** Expose the internal `TaskQueue` mechanism to the Flask API. Create `POST /queue/enqueue`, `GET /queue/dequeue`, and `POST /queue/status` to allow external agents or the UI to directly interact with the scheduler.

## 5. The "Kill Switch" (Emergency Stop)
- **Task:** Implement a `/kill` or `/pause` endpoint that instantly stops the task queue, pauses the `solomon_heartbeat.py` worker, and transitions the system state to `PAUSED_BLOCKED` to stop any runaway agents.

## 6. Telemetry & Observability Endpoint
- **Task:** Create a `GET /metrics` endpoint in `app.py` returning JSON statistics such as uptime, number of queue items pending, total active cards, and rolling average confidence scores for external monitoring (e.g. Grafana).

## 7. Autonomous Self-Reflection Job in Heartbeat
- **Task:** Update `solomon_heartbeat.py` to trigger a nightly or continuous background job that uses the `SemanticEmbedder` to scan the repository for duplicated, contradictory, or highly clustered Knowledge Cards, generating a summary report.

## 8. File Lock Synchronization for Queue (Enhanced SQLite Transactions)
- **Task:** Upgrade `solomon_knowledge_cards/storage/queue.py` to utilize explicit SQLite `BEGIN EXCLUSIVE` transactions or file-based locking to prevent race conditions when multiple dockerized workers attempt to dequeue tasks simultaneously.

## 9. Implement Automatic Procedure Card Mutation
- **Task:** Construct a specific API route or background script where an `ACTIVE` Repair Card will automatically generate a git branch containing proposed Markdown modifications to the original Procedure checklists.

## 10. Local MCP Server Spin-up Logic Framework
- **Task:** Implement a dynamic subprocess manager class in `app.py` or `solomon_heartbeat.py` capable of programmatically provisioning, starting, and monitoring local Model Context Protocol (MCP) servers as defined in the theoretical runtime specification.
