# Solomon OS: Governed De-restricting Runbook & Transition Blueprint

This document specifies the professional, strategic transition roadmap to securely unlock live, read-write, and autonomous execution capabilities across all of Solomon’s underlying helper engine pipelines. It outlines a mathematically governed **3-Phase Governed Capability Promotion Pipeline (GCPP)** to bridge the gap between Gabriel’s dynamic AST code assimilation and Mnemosyne’s SQLite-backed persistence, ensuring complete sandbox safety, static auditing, and automatic self-healing.

---

## 1. Executive Transition Philosophy

The Solomon Perpetual Learning Machine operates on a continuous 24/7 evolutionary cycle (Prometheus -> Gabriel -> Mnemosyne -> Loki). Letting automated agents modify code, execute binaries, and persist database modifications introduces systemic risks:
1. **Dynamic Execution Pollution:** Code dynamically patched in memory could cause runtime crashes or resource leaks.
2. **Database Corruption:** Unrestricted write capabilities could write malformed structures to SOK tables.
3. **Infinite Loops or Memory Creep:** Code optimization cycles might cause process memory to expand exponentially, exceeding hardware limits.

To solve this, Solomon implements a strict **Governed Capability Promotion Pipeline (GCPP)** that decouples rapid dynamic iteration from active production deployment. By default, helper workers are quarantined in high-safety `READ_ONLY` or `DRY_RUN_ONLY` modes. Transitioning them to `LIVE` or `READ_WRITE` must be done sequentially, verifying safety invariants at each milestone.

---

## 2. Worker Execution Modes Matrix

Solomon manages helper statuses in the SQLite `worker_modes` table. The transition matrix maps worker safety levels:

| Worker Name | Quarantined State (Default) | Active State (Live) | Description & Transition Safeguards |
| :--- | :--- | :--- | :--- |
| **Gabriel** | `READ_ONLY` | `READ_WRITE` / `LIVE` | Dynamic AST parser/compiler. In `LIVE` mode, the autonomous loop can execute real Git rollbacks, file modifications on disk, and class hot-swapping. |
| **Mnemosyne** | `READ_ONLY` | `READ_WRITE` | SOK database manager. Transition allows the agent to update knowledge cards and record execution traces on disk without proxy interception. |
| **Prometheus** | `DRY_RUN_ONLY` | `LIVE` | Continuous audit loop. Transition enables active database scanning, automated model routing modifications, and self-reflection updates. |
| **Loki** | `RESEARCH_ONLY` | `LIVE` | Sport Betting Intel & Command Board. Transition connects betting selection picks directly to active endpoint dispatchers. |

---

## 3. The Three-Phase Promotion Pipeline (GCPP)

### Phase 1: Local Sandboxing & Static Verification (DRAFT)
* **Objective:** Verify syntactic and architectural correctness of all newly assimilated capabilities.
* **Procedures:**
  1. **Sandbox Isolation:** Newly generated methods or clean-room Python classes are compiled in a temp file or isolated thread context.
  2. **Static Security Audits:** Run regex patterns and security AST parsers over code blocks to block imports of destructive modules (e.g., direct OS deletions or subprocess escapes).
  3. **Mock Executions:** Call the generated method with dummy variables and assert that return schemas conform to the expected specification.
  4. **Database State:** The new SOK card is stored in SQLite with status `DRAFT`.

### Phase 2: Governed Review & Verification (REVIEWED / APPROVED)
* **Objective:** Run targeted unit testing and promote capabilities to human/reviewer verification.
* **Procedures:**
  1. **Unit Testing:** Execute the pytest suite with the new capability active. Achieve 95%+ coverage on endpoints.
  2. **Review Gate Activation:** Trigger `/api/mnemosyne/review` to elevate the SOK card status from `DRAFT` to `REVIEWED` and then to `APPROVED`.
  3. **Audit Trail Logging:** Every promotion logs a datetime-stamped record in the SQLite `revisions` table, preserving the historical content of the card and its deterministic local embedding vector.

### Phase 3: Production Stabilization & Zero-Downtime Deployment (ACTIVE)
* **Objective:** Enable hot-swapping runtime execution with continuous resource telemetry tracking.
* **Procedures:**
  1. **Status Elevation:** Promote the card status to `ACTIVE`.
  2. **Zero-Downtime Hot-Reload:** Inject the approved class method programmatically on-the-fly using the `/api/mnemosyne/ast-inject` endpoint. The in-flight memory router immediately re-instantiates the active model-routing preferred layout with 0% dropped server requests.
  3. **Resource Telemetry Audit:** The `InfrastructureResourceMonitor` continuously monitors the process RSS memory footprint. If the RSS exceeds our **1.5 GB RAM cap**, a `CRITICAL_OVERLIMIT` warning is triggered, writing plain-text warnings to `logs/solomon_telemetry.log`.
  4. **Self-Healing Abort-and-Revert:** If a runtime crash or memory ceiling is hit, the Autonomous Improvement Loop (AIL) automatically reverts the affected Python file on disk using Git and triggers a rollback.

---

## 4. Runbook: Executing Worker Transitions

When promoting helper engines to active live status, follow these steps:

### Step 1: Query Current Helper Worker Status
Send a `GET` request to `/api/command-center/worker-modes` to inspect active states:
```bash
curl -X GET http://localhost:10000/api/command-center/worker-modes
```
Response:
```json
{
  "status": "success",
  "worker_modes": {
    "Gabriel": "READ_ONLY",
    "Mnemosyne": "READ_ONLY",
    "Prometheus": "DRY_RUN_ONLY",
    "Loki": "RESEARCH_ONLY"
  }
}
```

### Step 2: Transition Worker Mode to Live Execution
Send a `POST` request to `/api/command-center/worker-modes` to update Gabriel's mode to `READ_WRITE` or `LIVE`:
```bash
curl -X POST http://localhost:10000/api/command-center/worker-modes \
  -H "Content-Type: application/json" \
  -d '{"worker_name": "Gabriel", "execution_mode": "READ_WRITE"}'
```
Response:
```json
{
  "status": "success",
  "worker_name": "Gabriel",
  "new_execution_mode": "READ_WRITE",
  "message": "Successfully transitioned Gabriel execution mode to 'READ_WRITE'."
}
```

### Step 3: Verify the Persistence of the Change
Verify that the change has persisted into the SQLite relational database:
```bash
sqlite3 solomon_mnemosyne_demo.db "SELECT * FROM worker_modes WHERE worker_name='Gabriel';"
```
Expected output:
```text
Gabriel|READ_WRITE
```

---

## 5. Continuous Monitoring & Safety Limits

The perpetual machine must maintain strict system stability:
* **Memory Limits:** The process footprint is monitored via `/metrics`. Any RSS above 1.5GB triggers automated garbage collection and alerts.
* **SQL Query Speed:** Average database response speeds are audited inside `/metrics` under `average_query_response_time_ms`. Performance is optimized via dynamic indexing and `VACUUM` commands if query response exceeds 15ms.
