# PROJECT SOLOMON — COGNITIVE CORE OPERATIONS MANUAL
**Classification:** Governed Operational Protocol (SOSS/Mnemosyne)
**Revision Date:** July 28, 2026
**Maturity Standard:** Level 4/7 Governed Learning Core

---

## 1. THREE-COMPUTER INFRASTRUCTURE STRATEGY

Solomon operates across three isolated computer tiers to enforce segregation of execution, learning experiments, and promotion auditing:

### SS1: Production Brain (Main Gatekeeper)
*   **Role:** Runs the stable API gateway, dynamic planners, and executes approved skill packages.
*   **Write Constraints:** Direct code modification or unreviewed file importing is prohibited.
*   **Database:** Accesses `solomon_soss.db` and long-term memory blobs.

### SS2: Learning Laboratory (Dynamic Sandboxing)
*   **Role:** Performs behavioral simulations, parses dependencies, runs AST-based injections, and tests improvements under extreme fault injection scenarios.
*   **Isolation:** Quarantined from modifying production databases or calling production APIs directly.

### SS3: Independent Reviewer (Cryptographic Verification)
*   **Role:** Independently compiles, verifies, and runs reproducible unit and integration tests from a pristine environment state.
*   **Promotion Gate:** Signs valid capability packages with signed Merkle roots and publishes them back to SS1.

---

## 2. DISASTER RECOVERY DRILLS & REBOOT RECOVERY

In the event of network degradation, database corruption, or sudden machine loss, follow these sequential recovery protocols:

### A. Sudden Power Loss / Database Lock Recovery
1.  Verify the integrity of `solomon_soss.db` and related storage pools:
    ```bash
    python3 scripts/solomon_dx.py
    ```
2.  If database corruption is detected, stop all active services:
    ```bash
    sudo systemctl stop solomon-soss.service
    ```
3.  Restore the latest uncorrupted backup from `backups/`:
    ```bash
    cp backups/solomon_soss_backup_[timestamp].db solomon_soss.db
    ```
4.  Re-run integrity checks and restart SOSS services:
    ```bash
    python3 scripts/solomon_dx.py
    sudo systemctl start solomon-soss.service
    ```

### B. Machine Loss & Pure Re-provisioning Drill
1.  Clone a clean copy of the canonical `solomon` repository onto the replacement computer.
2.  Install system-level packages and initialize the localized virtual environment:
    ```bash
    python3 -m pip install -r requirements.txt
    ```
3.  Deploy systemd service configuration to automate startup recovery:
    ```bash
    sudo cp deploy/solomon-soss.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable solomon-soss.service --now
    ```

---

## 3. SCHEDULED COMPACTION & RETENTION POLICY

To prevent unbounded file growth and performance degradation:
*   **Compaction Frequency:** Once every 24 hours during idle phases, the background autonomic loop executes SQLite `VACUUM` and `ANALYZE` commands.
*   **Retention Period:**
    *   **Layer 0 (Working Memory):** TTL of 300 seconds. Overwrites or moves to Layer 1.
    *   **Layer 1 (Short-Term Memory):** Retained up to 24 hours before automatic paging consolidation to Layer 2.
    *   **Layer 2 (Long-Term Memory / Blob Store):** Saved permanently inside the cryptographically signed `solomon_brain_map.bin` blob.

---

## 4. API & GATEWAY CONTRACT SCHEMAS

All web-exposed SOSS endpoints are versioned under `v1` and enforce strict bearer token authorization:

*   `POST /api/memory/ingest` — Ingests a new episodic/factual memory atom.
*   `POST /api/memory/recall` — Executes Hybrid RAG search on long-term memory indices.
*   `POST /api/memory/dream` — Invokes non-blocking random walks over the sparse adjacency connectome.
*   `POST /api/governance/review` — Approves, denies, or quarantines procedural proposals.
