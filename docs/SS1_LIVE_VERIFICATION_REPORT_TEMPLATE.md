# SS1 Live Deployment & Verification Report

*Fill out this report after executing the live verification script on SS1.*

- **Date of Verification:** [YYYY-MM-DD]
- **Verification Performed By:** [Operator Name / Agent ID]
- **Status (Select One):**
  - `IMPLEMENTATION INCOMPLETE`
  - `IMPLEMENTED AND READY FOR SS1 DEPLOYMENT`
  - `DEPLOYED BUT LIVE VERIFICATION FAILED`
  - `DEPLOYED AND LIVE VERIFIED`

---

## 1. Environment Status Checklist

| Check Item | Result / Output | Status (PASS/FAIL) |
|---|---|---|
| Git Commit Deployed | [git rev-parse HEAD output] | |
| Systemd `solomon-api.service` | [active/inactive] | |
| Systemd `solomon-proxy.service` | [active/inactive] | |
| API Health (`GET :18789/api/health`) | [JSON response] | |
| Proxy Health (`GET :7420/api/health`) | [JSON response] | |
| Persistent Database File Path | `/srv/storage/toshiba/BubblePath/data/mnemosyne/solomon_mnemosyne.db` | |
| Initial Card Count | [integer count] | |

---

## 2. Ingestion & Promotion Verification

1. **Ingest Test Worker Report:**
   - Command:
     ```bash
     curl -X POST -H "Authorization: Bearer <KEY>" -H "Content-Type: application/json" \
       -d '{"report_id": "WR-TEST-999", "task_id": "TASK-999", "outcome": "SUCCESS", "attempted": "Simulate repair action on SS1 port crash.", "succeeded": "Fixed port collison.", "candidate_learning": true}' \
       http://127.0.0.1:7420/api/command-center/worker-report
     ```
   - Resulting Generated Draft Card ID: `KC-DRAFT-WR-TEST-999`
   - Status (PASS/FAIL):

2. **SS3 Review Promotion:**
   - Command:
     ```bash
     curl -X POST -H "Authorization: Bearer <KEY>" -H "Content-Type: application/json" \
       -d '{"card_id": "KC-DRAFT-WR-TEST-999", "reviewer": "SS3", "decision": "ACTIVATE", "notes": "Approved and activated live on SS1"}' \
       http://127.0.0.1:7420/api/command-center/review
     ```
   - Returned validation state: `ACTIVE`
   - Status (PASS/FAIL):

3. **Query Retrieval & Telemetry check:**
   - Command:
     ```bash
     curl -X POST -H "Authorization: Bearer <KEY>" -H "Content-Type: application/json" \
       -d '{"message": "How do we recover from port crash on SS1?", "conversation_id": "C-999", "request_id": "R-999", "security_classification": "INTERNAL"}' \
       http://127.0.0.1:7420/api/command-center/solomon-chat
     ```
   - Confirm returned memory contains `KC-DRAFT-WR-TEST-999`:
   - Status (PASS/FAIL):

4. **Persistence after Service Restart:**
   - Restart command:
     ```bash
     sudo systemctl restart solomon-api.service
     ```
   - Repeat the query:
   - Confirm returned memory contains `KC-DRAFT-WR-TEST-999` after restart:
   - Status (PASS/FAIL):

5. **Deprecate Synthetic Test Card:**
   - Deprecation command:
     ```bash
     curl -X POST -H "Authorization: Bearer <KEY>" -H "Content-Type: application/json" \
       -d '{"card_id": "KC-DRAFT-WR-TEST-999", "reviewer": "SS3", "decision": "DEPRECATE", "notes": "Cleanup synthetic test card"}' \
       http://127.0.0.1:7420/api/command-center/review
     ```
   - Status (PASS/FAIL):
