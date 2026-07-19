# Project Mnemosyne: Security Threat Model & Mitigation Strategy

This document outlines key security threats identified for Solomon's Memory Card Engine and provides mitigation strategies for production deployments.

---

## 1. Threats, Vectors & Mitigations

### Threat A: Memory Poisoning & Injection Persistence
- **Vector:** A compromised worker or malicious output generates false, misleading, or destructive Knowledge Cards (e.g. injecting malicious shell commands or false API instructions into a playbooks's `repair_action`).
- **Impact:** Future workers retrieve the poisoned card, execute the malicious instructions, leading to system hijack, privilege escalation, or corrupted runs.
- **Mitigation:**
  1. **Strict Review Gate (SS3 Governance):** All extracted cards remain in `DRAFT` or `PENDING_REVIEW` state and can never be retrieved as trusted guidance.
  2. **Human-in-the-Loop or Governed SS3 Authorization:** Cards must be reviewed and promoted through `REVIEWED` and `APPROVED` stages by authorized keys/operators before transition to `ACTIVE`.
  3. **Strict Validation Checks:** Markdown parser strips dangerous shell redirects, sanitizes input strings, and validates schema compliance.

### Threat B: Privilege Escalation via Unauthorized Metadata Manipulation
- **Vector:** A low-privilege worker injects high-security labels (`CONFIDENTIAL`, `SECRET`) or changes state fields directly.
- **Impact:** Denial of service, or exposure of restricted procedural information.
- **Mitigation:**
  1. **Provenance Tracking:** Every card update requires an explicit `created_by` or `updater` signature.
  2. **Revision Logs:** Any status or metadata alteration is appended to an immutable audit table (`card_revisions`) with full traceability. Historical records cannot be updated.

### Threat C: Protected Information Leakage (Data Spillage)
- **Vector:** An internal worker processes sensitive data (API keys, client credentials, PII) and writes them into `evidence` or `body` of a Knowledge Card, which is then indexed.
- **Impact:** Sensitive leaks are retrieved and exposed in query responses to unauthorized workers or external APIs.
- **Mitigation:**
  1. **Lexical Regex Filtering:** The extraction engine runs preprocessing pattern filters on worker reports to strip API keys (`sk-...`, passwords, credential strings).
  2. **Security Classification Filtering:** The repository search API supports active security-classification filters. Low-clearance queries cannot retrieve `RESTRICTED` or `INTERNAL` labeled cards.

### Threat D: Database Corruption & Denial of Service (DoS)
- **Vector:** Rapid parallel writes from infinite worker loops lock the SQLite file or corrupt tables.
- **Impact:** System downtime or memory loss.
- **Mitigation:**
  1. **Thread-Safe Locks:** Reentrant `RLock` serializes writes in python, making the DatabaseManager connection completely thread-safe.
  2. **Busy Timeout Control:** Configured `PRAGMA busy_timeout = 10000;` ensures SQLite handles transient lock contention gracefully without throwing abort errors.
  3. **Automated JSONL Backups:** Built-in JSONL exports facilitate routine point-in-time snapshots for fast disaster recovery.
