# Solomon Engine Registry

This registry provides an inventory of all active, disabled, internal, and generated engines in the Solomon repository.

## Registry Capability Schema
Every registered capability includes:
- **Version:** Module version tracking.
- **Description:** Human-readable intent.
- **Inputs/Outputs:** Defined interface boundaries.
- **Required Permissions:** Needed runtime permissions.
- **Dependencies:** Explicitly listed dependencies.
- **Health State:** Current health monitoring status.
- **Last Validation Time:** ISO timestamp of last registry test.
- **SS Classification:** Swarm Service Tier (SS1/SS2/SS3).

## Group: joe_jules

| Engine ID | Status Class | Route/Readiness | Version | SS Class | Health | Next Action |
|---|---|---|---|---|---|---|
| `solomon_joe_bridge` | `approval_blocked` | `/api/joe/status`, `/api/joe/queue-blueprint` | `1.0.0` | `SS2` | `healthy` | Maintain functionality |
| `joe_blueprint_facade` | `active_route` | `/api/joe/queue-blueprint` | `1.0.0` | `SS2` | `healthy` | Maintain functionality |
