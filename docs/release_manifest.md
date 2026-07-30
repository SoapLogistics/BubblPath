# 📦 Solomon Release & Versioning Manifest

This manifest outlines current component versions, API schemas, rollback guidelines, and database migration ordering rules for the SOSS environment.

---

## 🔢 Component Version Map

| Subsystem | Version | Status | Primary File |
|---|---|---|---|
| **SOSS Gateway API** | `1.4.0` | Active | `app.py` |
| **Mnemosyne Memory** | `2.1.0` | Active | `core/solomon_quantized_memory.py` |
| **Gabriel Evolution Lab** | `2.0.2` | Simulated Sandbox | `gabriel_engine/core/` |
| **Prometheus Futures** | `2.0.0` | Active / Real Math | `services/solomon_futures_engine.py` |
| **MD6 Governance Gate** | `1.5.0` | Active | `services/solomon_governance_approval_packet.py` |

---

## 🗄️ Database Schemas & Migrations

### Migration Ordering Rules:
1.  **Stage 1: Core Memory Tables** (`solomon_hyper_memory.db`) must be initialized before any other subsystems load. Ensure `memory_atoms` are mapped with compressed content blobs.
2.  **Stage 2: Futures Engine Tables** (`solomon_soss.db`) are created to store Monte Carlo simulation records, enabling idempotency checks.
3.  **Stage 3: Zero-Copy Governance Logs** (`governance_log.bin`) are verified via sequential hash chaining at startup to detect history tampering.

### Transaction Policies:
-   All database connections must set `timeout=10.0` to avoid locking.
-   WAL (Write-Ahead Logging) must be configured on all SQLite databases via `PRAGMA journal_mode=WAL;`.

---

## 🛡️ Rollback & Deployment Checklist

### Pre-Deployment Verification:
- [ ] Run style lint: `./scripts/solomon_dx.py lint`
- [ ] Run test suite: `./scripts/solomon_dx.py test`
- [ ] Verify system health: `./scripts/solomon_dx.py health-check`
- [ ] Confirm no uncommitted code or active dirty state in working tree.

### Post-Deployment Verification:
- [ ] Verify gateway serves requests on Port 10000.
- [ ] Execute a smoke recall query to ensure `solomon_hyper_memory.db` connections resolve.
- [ ] Verify `verify_integrity()` returns `True` for the governance log file.

### Rollback Points:
In the event of a deployment failure (e.g., integrity mismatch or database deadlock):
1.  **Step 1:** Stop server process immediately.
2.  **Step 2:** Rollback to stable git tag (e.g. `v1.3.9-stable`).
3.  **Step 3:** Re-run the tests to confirm success.
4.  **Step 4:** Restart server process.
