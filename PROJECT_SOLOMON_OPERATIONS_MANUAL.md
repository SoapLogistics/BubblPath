# Solomon central systems & three-computer infrastructure operations manual
**Document Version:** 1.0.0
**Target Infrastructure:** SS1 (Production), SS2 (Learning Lab), SS3 (Gatekeeper)
**Status:** Canonical & Active

---

## 1. Executive overview of three-computer infrastructure
Solomon operates across three dedicated computer nodes (SS1, SS2, and SS3) connected securely over Tailscale and SSH to form a governed, fault-tolerant, autonomous system.

### 1.1 Machine roles & division of responsibility
*   **SS1 — Production Brain (Staging & Live Execution):**
    *   **Core Role:** Runs the validated and promoted SOSS Central Reasoning Engines, Solomon Reasoning, APIs, proxies, and live user communication surfaces.
    *   **Restriction:** Dynamic capability learning/execution is strictly banned from direct execution here. Only immutable, approved, and cryptographically verified skill packages from SS3 can be ingested or run.
*   **SS2 — Learning Laboratory (Candidate Discovery & Experimentation):**
    *   **Core Role:** Runs the autonomous crawlers, Gabriel Perpetual Intake loops, structural scan engines, dependency scanners, and behavioral sandboxes.
    *   **Restriction:** Highly sandboxed environment with lease controls, execution limits, and strict RCE prevention.
*   **SS3 — Reviewer, Auditor & Cryptographic Gatekeeper:**
    *   **Core Role:** Holds final promotion decision authorities. Implements Crucible test replicability checks, compliance scanners, security regression audits, licensing gates, and the zero-copy Merkle hash ledger.
    *   **Restriction:** Only SS3 can sign promotions and write to the immutable append-only governance log (`governance_log.bin`).

### 1.2 Networking & identity specifications
*   **Subnet Configuration:** Static private interfaces routed over Tailscale interfaces (`100.64.0.0/10`).
*   **Hostnames:** `ss1-machine.tailscale`, `ss2-machine.tailscale`, `ss3-machine.tailscale`.
*   **Ports & Firewall rules (UFW):**
    *   `Port 22/tcp` (SSH) restricted to Tailscale admin subnet.
    *   `Port 7420/tcp` (Node.js Edge Proxy) open internally.
    *   `Port 10000/tcp` and `Port 18789/tcp` (SOSS central backend) bound strictly to `127.0.0.1`.
*   **Key Rotation:** SSH keys must use Ed25519 with 24-hour cron audit to verify `authorized_keys` integrity and evict unknown public keys.

---

## 2. Service and daemon maintenance
Each service running on SOSS is managed under systemd and governed by explicit resource caps, automated sandboxing, and strict failure/backoff loops.

### 2.1 Service inventory
1.  **`solomon-soss.service` (Central Engine):** Central nervous system running Flask interface and memory/context routing.
2.  **`solomon-kac-daemon.service` (Knowledge Assimilation Center):** Persistent background worker executing the ingestion queue.
3.  **`solomon-loki-scanner.timer` (Loki Futures Scheduler):** Systemd timer executing daily scan projections.

### 2.2 Systemd template specifications (`/lib/systemd/system/solomon-soss.service`)
```ini
[Unit]
Description=Solomon Secure Operations System (SOSS) Central Engine
After=network-online.target local-fs.target
Requires=network-online.target

[Service]
Type=simple
User=solomon
Group=solomon
WorkingDirectory=/opt/solomon/soss
EnvironmentFile=/etc/solomon/soss.env
ExecStart=/opt/solomon/venv/bin/python app.py

# Graceful Shutdown
KillMode=control-group
TimeoutStopSec=30
SendSIGKILL=yes

# Restart Limits and Backoff
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=5

# Hard Resource Limits
CPUQuota=50%
MemoryMax=2000M
LimitNOFILE=65536
```

### 2.3 Daemon health & watchdog policies
*   **No Restart Loops:** If a daemon fails 5 times within 60 seconds, systemd marks it as failed rather than entering a CPU-intensive infinite loop.
*   **Graceful Shutdown:** On `SIGTERM`, services have a 30-second window to close active database connections, flush memory outboxes, write checkpoints, and log final shutdown traces.

---

## 3. Backup and recovery procedures
SOSS implements a strict separation between code backup (managed via Git and remote mirrors) and dynamic data backup (sqlite DBs, keys, and mmap logs).

### 3.1 Backed up assets inventory
*   **Databases:** `solomon_soss.db`, `solomon_hyper_memory.db`, `memory_atoms.db` (SQLite state).
*   **Memory Records:** `solomon_brain_map.bin` (L2 Long-term binary memory vector).
*   **Configuration Files:** All YAML/JSON rules in `config/` and `solomon_api/`.
*   **Audit logs:** `governance_log.bin` (promotion chains).

### 3.2 Automated rotation & compression (`backup_manager.sh`)
The system retains the last **7 daily backups** under `/var/backups/solomon/` in compressed gzip format. Each backup is accompanied by a SHA-256 signature verification file to prevent silent archive corruption.

### 3.3 Disaster recovery runbook (Clean machine restore)
In the event of physical or hardware failure:
1.  **Provision Target Hardware:** Ensure Python 3.12, sqlite3, and system packages are installed.
2.  **Restore Directory Structure:** Create `/opt/solomon/soss` with correct `solomon` owner permissions.
3.  **Fetch Backup Archive:** Pull the latest verified backup from the remote backup host.
4.  **Verify Checksum:**
    ```bash
    sha256sum -c solomon_backup_YYYYMMDD_HHMMSS.tar.gz.sha256
    ```
5.  **Extract Data Assets:**
    ```bash
    tar -xzf solomon_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/solomon/soss/ --strip-components=1
    ```
6.  **Validate DB Integrity:**
    ```bash
    sqlite3 /opt/solomon/soss/solomon_soss.db "PRAGMA integrity_check;"
    ```
7.  **Launch Service:** Start systemd unit and verify system logs.

---

## 4. Comprehensive verification & testing protocol
SOSS uses rigorous deterministic test coverage running inside clean-room environments.

### 4.1 Test catalog & purpose
*   **Unit & Integration Tests (`tests/test_real_perpetual_learning_cycle.py`):** Ensures complete closed-loop learning correctness (Task failure -> duplicate check -> approval -> retrieve -> success -> outcome score).
*   **Engine Registry Verification (`tests/test_engine_registry.py`):** Prevents anonymous or unregistered services from running in production.
*   **Threshold Simulation Gates (`tests/futures/test_threshold_logic.py`):** Validates the Monte Carlo 90+ confidence checks and Wilson lower bounds.
*   **Resilience and Security Tests (`tests/test_system_resilience.py`):** Validates checksum recovery, SS3 bypass blocks, network failure tolerance, and database integrity.

### 4.2 Test execution
To run the full suite cleanly, execute:
```bash
PYTHONPATH=. python3 -m pytest -v
```
All test artifacts must be cleaned up dynamically post-test to keep the local filesystem unpolluted. Live production data must never be altered during test runs.
