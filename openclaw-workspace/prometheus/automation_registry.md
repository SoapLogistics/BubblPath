# Automation Registry

*Last Synced: 2026-07-19 18:32:53 UTC*

This registry identifies manual operational steps and classifies their progress toward fully governed automation.

| Procedure Name | ID | Type | Implementation Mode | Status |
| :--- | :--- | :--- | :--- | :--- |
| Gateway Health Check | `PC-AC-01.1` | Diagnostic | Manual Markdown Check | **Candidate** |
| Hourly Git State Sync | `PC-AC-01.3` | Operations | Manual Git Commit | **Candidate** |
| Open-Source Code Scan | `PC-SO-01.2` | Growth | Manual Regex/Grep scan | **Candidate** |
| Prometheus Audit Sync | `PC-PR-01` | Architecture | Programmatic Script Run | **Automated** |

## Automation Lifecycle States
- **Candidate:** Manual process defined clearly in a checklist.
- **Verified:** Script or program completes task in isolated environment.
- **Automated:** Triggered automatically via cron, hook, or API event.
- **Governed:** Task outputs are verified via automated Review Gates before file commitment.
