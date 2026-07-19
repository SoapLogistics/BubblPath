# MASTER PROCEDURE CARD: 24/7 Autonomous Cycle & State Synchronization

- **Card ID:** PC-AC-01
- **Focus Area:** Master Lifecycle Control, Scheduling, State Persistence, and System Self-Healing
- **Target Agent:** OpenClaw Primary Coordinator (BubbleBot)
- **Lifecycle Mode:** 24/7 Continuous Execution

---

## 1. Context & Purpose
This procedure card serves as the master protocol for the continuous, 24/7 autonomous lifecycle of the BubblePath platform. It provides exact step-by-step instructions for scheduling heartbeat tasks, persisting and restoring state across asynchronous turns, running background diagnostic tasks, performing automated self-healing, and writing daily handover notes.

---

## 2. Operational Checklist

### Phase 1: Heartbeat Trigger & Environmental Check
The master loop triggers on a persistent interval (every 10 minutes). On each trigger, perform the following environmental checks:
- [ ] **1.1 Resource Capacity Check:** Execute a disk space check. Verify that free space is above 15%:
  ```bash
  df -h /srv/storage
  ```
- [ ] **1.2 Memory Audit:** Verify memory footprint is stable:
  ```bash
  free -m
  ```
- [ ] **1.3 Network Connection Check:** Verify internal networks and key external API gateways (OpenAI, OpenHands, CrewAI) are reachable:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models
  ```

### Phase 2: State Synchronization & Resumption
Since execution is asynchronous and state can reset between sessions, the agent must rebuild its "mental model" before running new actions:
- [ ] **2.1 Read Handover Notes:** Locate the daily progress log inside the memory folder and read the previous turn's output:
  ```bash
  cat /srv/storage/toshiba/BubblePath/openclaw-workspace/memory/$(date -d "yesterday" +%Y-%m-%d).md 2>/dev/null || cat /srv/storage/toshiba/BubblePath/openclaw-workspace/memory/$(date +%Y-%m-%d).md 2>/dev/null
  ```
- [ ] **2.2 Parse Task Queue:** Inspect `/srv/storage/toshiba/BubblePath/openclaw-workspace/task_queue.json` for active, pending, or stalled tasks.
- [ ] **2.3 Git Branch Consistency:** Ensure the workspace is aligned to the correct active git branch, clean up lockfiles, and run a fast pull from the backup remote:
  ```bash
  git fetch origin && git status
  ```

### Phase 3: Background Tasks & Heartbeat Operations
Run the scheduled tasks configured under the active time window (refer to `HEARTBEAT.md` for frequencies):
- [ ] **3.1 Sync Logs (Hourly):** Push active progress files and heartbeat status logs to the remote repository.
- [ ] **3.2 Run Cleanup (Six-Hourly):** Clear stale docker artifacts, unused volumes, and expired temporary cache files:
  ```bash
  docker system prune -f --volumes
  ```
- [ ] **3.3 Compile Report (Daily):** Roll log files and assemble the daily report digest.

### Phase 4: Self-Healing & Auto-Recovery
If a sub-agent (OpenHands or CrewAI) or a background service encounters a failure:
- [ ] **4.1 Auto-Remediation:** If a docker container exited unexpectedly, trigger an automated restart:
  ```bash
  docker restart openhands-runner || docker run -d --name openhands-runner ...
  ```
- [ ] **4.2 Backoff Delay:** Introduce an incremental cool-down delay (30s) before resuming task execution to allow resources to stabilize.
- [ ] **4.3 Database Restoration:** If a localized database or state file is corrupted, restore it from the most recent backup file:
  ```bash
  cp state.json.backup state.json
  ```
- [ ] **4.4 Process Cleanup:** Terminate hung processes and orphaned subprocesses to free up CPU threads.

### Phase 5: Daily Handover & Logging
Before concluding the current execution cycle:
- [ ] **5.1 Write Progress Log:** Create or append to the daily progress file `/srv/storage/toshiba/BubblePath/openclaw-workspace/memory/YYYY-MM-DD.md`.
- [ ] **5.2 Structure Handover Payload:** Ensure the log contains:
  - **Timestamp:** Current execution completion time.
  - **Status of Services:** Port/endpoint health status.
  - **Completed Tasks:** Successful accomplishments during this turn.
  - **Pending Backlog:** Specific tasks remaining for the next turn.
  - **Next-Turn Instructions:** Explicit prompt instructions directing the next agent invocation.
- [ ] **5.3 Append to Audit Trail:** Update `/srv/storage/toshiba/BubblePath/openclaw-workspace/heartbeat.log` with the final status code of the heartbeat execution (`SUCCESS` or `PAUSED_BLOCKED`).
