# PROCEDURE CARD: OpenHands Integration & Operational Checklist

- **Card ID:** PC-OH-01
- **Focus Area:** Software Engineering, Codebase Maintenance, and Repository Interactivity
- **Target Agent:** OpenHands (Sub-Agent Engine)
- **Lifecycle Mode:** 24/7 Autonomous execution

---

## 1. Context & Purpose
This procedure card guides the OpenClaw coordinator through initiating, tracking, verifying, and recovering OpenHands coding sessions. OpenHands must only be engaged for multi-file code modifications, test suite troubleshooting, dependency repairs, or automated package upgrades.

---

## 2. Operational Checklist

### Phase 1: Pre-Execution Verification
Before starting any OpenHands session, the OpenClaw coordinator must execute and confirm the following:
- [ ] **1.1 Sandbox Health Check:** Verify the Docker daemon is active:
  ```bash
  docker info
  ```
- [ ] **1.2 Repository Isolation:** Avoid dirty trees. Create a new git branch for the task:
  ```bash
  git checkout -b openhands-task-<task_id>
  ```
- [ ] **1.3 Environment Check:** Verify that `OPENHANDS_URL` and `OPENHANDS_API_KEY` are populated in the environment.

### Phase 2: Session Invocation
Deploy the OpenHands workspace using the `openhands_run` tool.
- [ ] **2.1 Configuration Payload:** Format the invocation request exactly as defined in `TOOLS.md`:
  ```json
  {
    "task": "Fix the outstanding bug in /app/app.py concerning error response validation.",
    "repo_path": "/srv/storage/toshiba/BubblePath/openclaw-workspace/",
    "model": "gpt-4o"
  }
  ```
- [ ] **2.2 Activity Monitoring:** Stream or read logs from the OpenHands container periodically. Check for progress and prevent infinite loop states:
  ```bash
  docker logs --tail 20 openhands-runner
  ```
- [ ] **2.3 Run Timeout Gating:** Apply a hard timeout limit of 900 seconds (15 minutes). If the execution exceeds this limit, trigger Phase 4 immediately.

### Phase 3: Verification & Integration
Once the OpenHands runner claims the task is complete:
- [ ] **3.1 Fetch Changes:** Inspect the files modified by OpenHands inside the mounted workspace. Run git status and diff:
  ```bash
  git status && git diff
  ```
- [ ] **3.2 Syntax & Linter Validation:** Run the appropriate local linter or compiler tool on modified files to verify no syntax bugs were introduced (e.g., `python -m py_compile <file.py>`).
- [ ] **3.3 Test Suite Execution:** Execute any existing regression or unit tests to ensure functional correctness.
- [ ] **3.4 Commit & Merge:** If verification passes:
  - Commit the changes on the task branch with a detailed git message.
  - Merge the task branch back into the active integration branch.
  - Delete the task branch to keep the tree clean.

### Phase 4: Failure Recovery & Self-Healing
If OpenHands encounters an unresolvable error, hangs, or fails the verification phase:
- [ ] **4.1 Graceful Cleanup:** Stop and remove the hung OpenHands Docker container to free resources:
  ```bash
  docker stop openhands-runner && docker rm openhands-runner
  ```
- [ ] **4.2 Code Rollback:** Reset the codebase to the last known-good state to clear corrupted modifications:
  ```bash
  git checkout main -- .
  git branch -D openhands-task-<task_id>
  ```
- [ ] **4.3 Retry Protocol:** If the error is a transient timeout, retry exactly once with a more specific, narrowed task prompt.
- [ ] **4.4 Human Escalation:** If the retry fails or the codebase remains broken, record details in `ERROR_STATE.md` and transition the task state to `PAUSED_BLOCKED`.
