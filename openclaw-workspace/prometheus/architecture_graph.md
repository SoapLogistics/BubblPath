# Architecture Graph

*Last Synced: 2026-07-20 09:47:32 UTC*

## Logical System Topology Diagram

This graph illustrates the system boundaries, communication protocols, and data pathways of Solomon's components.

```
       SS1 (Lightweight Ingress API)
       ┌───────────────────────────┐
       │     Flask App (app.py)    │
       └─────────────┬─────────────┘
                     │ (Delegates Task Cards)
                     ▼
       SS2 (Execution & Worker Compute Server)
       ┌───────────────────────────┐
       │     Task Queue Engine     │ <── [OpenHands Engine (PC-OH-01)]
       └─────────────┬─────────────┘ <── [CrewAI Orchestration (PC-CA-01)]
                     │ (Aggregates Review Packets)
                     ▼
       SS3 (Cognition, Governance & Self-Evolution)
       ┌───────────────────────────┐
       │   Knowledge Card Engine   │ ──> Writes [Knowledge Cards]
       │   Prometheus Monitoring   │ ──> Writes [Strategic Roadmap]
       └───────────────────────────┘
```

## Graph Integrity Constraints
1. **Unidirectional Execution Flow:** No worker in SS2 should modify SS3 governance policies without passing the automated Review Gate.
2. **Gateway Sandboxing:** Flask endpoint must not mount execution system volumes directly.
3. **No Direct Secret Access:** External integrations query the local credential vault on SS3 rather than storing local key vectors on SS1.
