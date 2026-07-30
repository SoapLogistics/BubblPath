# 🛠️ SOSS Multi-Computer Operations Manual

This document provides the canonical guidelines and operational recovery runbooks for executing SOSS across a three-computer strategy (SS1, SS2, and SS3).

---

## 🏛️ Machine Roles & Specifications

### 🖥️ **SS1 — Production Brain (Staging & Gateway)**
*   **Role:** Runs the live unified SOSS API gateway, responds to CNS queries, and executes approved/promoted capabilities.
*   **Access Policy:** Read-only for database schemas, signature-gated for dynamic module compilation.
*   **Running Services:**
    -   SOSS Flask Gateway (Port 10000)
    -   API Proxy Interceptor (Port 7420)

### 🖥️ **SS2 — Learning Laboratory (AST Execution & Sandbox)**
*   **Role:** Performs static program deconstructions, dynamic capability testing, and evolutionary optimization.
*   **Access Policy:** Sandbox-isolated filesystem access and bounded environment parameters.

### 🖥️ **SS3 — Independent Auditor (MD6 Verification Gate)**
*   **Role:** Holds authority for final promotion signatures, audits zero-copy transaction logs, and runs verification checks.
*   **Database state:** Holds canonical signature databases and verification scripts.

---

## 🔄 Automated Backup & Integrity Recovery

SOSS maintains thread-safe SQLite backups and chained governance logs to guarantee complete disaster recovery.

### 1. Database Backup Strategy
-   Backups of `solomon_hyper_memory.db` and `solomon_soss.db` are generated daily.
-   Each backup is stored alongside a SHA-256 checksum to detect file corruption or tampering.

### 2. Hash-Chain Log Integrity Verification
-   The zero-copy binary log `governance_log.bin` is cryptographically chained.
-   At every server startup, `verify_integrity()` is executed sequentially to ensure no transactions were inserted, deleted, or altered.

---

## 🚨 Disaster Recovery Procedures

### Scenario A: SQLite Database Corruption Detected
1.  **Step 1:** Stop SOSS services: `./scripts/solomon_dx.py stop` (or kill the active process).
2.  **Step 2:** Check integrity:
    ```bash
    sqlite3 solomon_hyper_memory.db "PRAGMA integrity_check;"
    ```
3.  **Step 3:** If corruption is found, restore from the latest stable daily backup file:
    ```bash
    cp backups/solomon_hyper_memory_backup.db solomon_hyper_memory.db
    ```
4.  **Step 4:** Restart SOSS gateway and confirm health checks:
    ```bash
    ./scripts/solomon_dx.py health-check
    ```

### Scenario B: Governance Hash-Chain Tampering Detected
1.  **Step 1:** If startup fails with `verify_integrity() -> False`, lock all SS1 execution immediately.
2.  **Step 2:** Query the event logs to pinpoint the index where the recorded block hash does not match the computed hash of the prior slot.
3.  **Step 3:** Revoke the compromised actions and rebuild the audit trail logs from the SS3 independent node.
