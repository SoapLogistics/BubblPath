# USER.md - Operator Profile & Escalation Guidelines

This file contains profiles and guidelines for communicating with the human owner/operator of the BubblePath platform.

---

## 1. User Profile
- **Primary Owner:** Lead Systems Architect
- **Relationship Type:** Collaborative Director
- **Communication Style Preference:** Bullet points, explicit command outputs, code blocks, zero conversational fluff.

---

## 2. Notification Preferences
- **Daily Summaries:** Deliver at 09:00 UTC detailing accomplishments, service status, and pending tasks from the last 24 hours.
- **Immediate Notifications:** Send alerts for any of the following conditions:
  - Docker container exits or failure to start OpenHands/CrewAI.
  - Disk capacity on `/srv/storage` exceeding 85%.
  - Execution runtime errors that block the heartbeat loop.

---

## 3. Escalation Rules

```
     ┌─────────────────────────────────────────────────────┐
     │                Unexpected Failure State             │
     └──────────────────────────┬──────────────────────────┘
                                │
             ┌──────────────────┴──────────────────┐
             ▼                                     ▼
     [Auto-Remediable]                     [Non-Remediable / Safety]
     - Timeout                              - Disk Full (>90%)
     - Temporary API 5xx                    - Broken Dependency Tree
     - Restartable Service                  - Conflicting Workspace State
             │                                     │
             ▼                                     ▼
┌───────────────────────────┐            ┌───────────────────────────┐
│ Run Self-Healing Sequence │            │ Transition to PAUSED state│
│ (Max 3 Retry Attempts)    │            │ Alert Operator Immediately│
└───────────────────────────┘            └───────────────────────────┘
```

- **Level 1 (Self-Healing):** In the event of a timeout or tool crash, attempt up to 3 automatic retries with incremental backoff (30s, 60s, 120s).
- **Level 2 (State Handover & Alert):** If Level 1 fails or if the error involves database corruption, dependency conflicts, or disk exhaustion (>90%):
  1. Record current memory context in `/srv/storage/toshiba/BubblePath/openclaw-workspace/ERROR_STATE.md`.
  2. Transition task state to `PAUSED_BLOCKED`.
  3. Send an immediate push/chat notification to the operator with logs.
