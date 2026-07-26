# Solomon Engine Registry

This registry provides an inventory of all active, disabled, internal, and generated engines in the Solomon repository.

## Group: joe_jules

| Engine ID | Status Class | Route/Readiness | Doc | Test | Blockers | Next Action |
|---|---|---|---|---|---|---|
| `solomon_joe_bridge` | `approval_blocked` | `/api/joe/status`, `/api/joe/queue-blueprint` | `docs/solomon_joe_bridge.md` | `tests/integration/solomon_joe_bridge_smoke.py` | duplicate backend/services import collision, subprocess launches jules CLI, repo allowlist missing | Resolve blockers to allow limited dry-run usage. |
| `joe_blueprint_facade` | `active_route` | `/api/joe/queue-blueprint` | `docs/joe_blueprint_facade.md` | `tests/test_joe_blueprint_facade.py` | None | Maintain proxy routing for dry-run capabilities. |