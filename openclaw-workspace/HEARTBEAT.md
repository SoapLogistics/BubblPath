# HEARTBEAT.md - Periodic Check Routines

This file is processed on every heartbeat execution. Keep it under 50 lines of compact, high-efficiency Markdown to conserve token usage.

---

## 1. Scheduled Heartbeat Routines

| Frequency | Task / Routine Name | Expected Action / Command |
| :--- | :--- | :--- |
| **Every 10m** | Baseline Health Check | Query endpoints, memory consumption, Docker daemon status. |
| **Every 1h** | Git State Sync | Commit `memory/` folder logs and push to backup repository. |
| **Every 6h** | Resource Audit | Check disk capacity on `/srv/storage` and purge temporary build artifacts. |
| **Every 24h** | Rollover & Report | Roll log files, compile daily progress, and send user summary. |

---

## 2. Heartbeat Execution Checklist

- [ ] 1. Verify `docker ps` returns active, healthy status for OpenHands & CrewAI runners.
- [ ] 2. Check disk usage is under 85% via `df -h /srv/storage`.
- [ ] 3. Scan system error logs (`journalctl` or container logs) for anomalous behavior.
- [ ] 4. Sync local workspace state and pending git commits to the upstream backup remote.
- [ ] 5. Write the heartbeat status directly to `/srv/storage/toshiba/BubblePath/openclaw-workspace/heartbeat.log`.
