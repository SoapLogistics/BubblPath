# State Store Inventory Audit

This document is the authoritative record of all persistent and active state stores, databases, logs, and pre-allocated binary structures detected within the active Project Solomon repository workspace.

---

## 1. Store Registry

### A. SQLite State Candidate (`memory_atoms.db`)
- **File Location:** `./memory_atoms.db`
- **File Size:** 12,288 bytes
- **Writer(s):** `services/q_result_verifier.py` (when present), capability modules (e.g. `renewable_worker_lease.py`, `codex_kanban.py`).
- **Reader(s):** Gabriel loop test suites, backend facading templates, and API endpoints.
- **Physical Schema (Reality Check):**
  ```sql
  CREATE TABLE memory_atoms (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      packet_id TEXT,
      memory_type TEXT,
      result TEXT,
      lesson TEXT
  );
  ```
- **Durability Model:** SQLite local transaction-backed storage.
- **WAL Status:** Default rollback journal. WAL is *not* enabled on this specific file by default.
- **Busy Timeout:** Not configured at the database driver connection level within legacy Gabriel modules (can lock under high-throughput concurrent tests).
- **Migration Ownership:** None. There are no migration records or schema version controls active for `memory_atoms.db` (it is handled as a lightweight local store/fixture).
- **Corruption Behavior:** Standard SQLite file lock corruption risks if processes terminate abruptly during lock transitions.

---

### B. Governance Binary Log (`governance_log.bin`)
- **File Location:** `./governance_log.bin`
- **File Size:** 65,536 bytes (pre-allocated)
- **Writer(s):** `services/solomon_governance_approval_packet.py` (via `GovernanceApprovalLane.log_transaction`).
- **Reader(s):** Verification tools and manual diagnostic inspections.
- **Physical Structure:**
  - Written using Python `struct` packing (`'256s'`).
  - Total occupied non-zero content: 87 bytes.
  - Repeating sequence: `refused`, `unknown`, `approved`, `unknown` written linearly across slots.
- **Durability Model:** Direct raw binary file appending/seeking with zero journaling or transaction safeguards.
- **WAL Status:** N/A (non-relational binary).
- **Migration Ownership:** None. Raw byte structure layout is hardcoded in the source file, making schema upgrades destructive without full file wipe.
- **Corruption Behavior:** Partial writes can corrupt subsequent alignment-based structural offsets.

---

### C. Active Event Text Log (`fact_memory.log`)
- **File Location:** `./fact_memory.log`
- **File Size:** 59 bytes
- **Writer(s):** `services/solomon_futures_engine.py` (Loki engine threshold events).
- **Reader(s):** Local test suite and log scrapers.
- **Physical Structure:** Single line plain-text append-only timestamped trace.
  ```text
  [1785125432.532834] Threshold 90.0 crossed with value 90.5
  ```
- **Durability Model:** standard Python append stream (`open(..., "a")`).
- **Corruption Behavior:** Line truncation if process terminates during append buffer flush.

---

## 2. Integrity and Backup Auditing

- **Test Databases:** No separate test database isolation exists for legacy Gabriel tests; they modify the active root directory database directly, risking side effects on sequential runs.
- **Backup Verification:** No automated backup schedules or rotation engines are configured. All state resides on unprotected host paths.
