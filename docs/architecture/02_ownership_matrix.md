# Subsystem Ownership Matrix

This matrix establishes canonical ownership and prevents duplicated responsibilities across the Solomon architecture.

| Subsystem | Owner / Role | Primary Responsibility | Interface / Storage |
|---|---|---|---|
| **Mnemosyne** | Cognitive Substrate | Governed long-term memory, card ingestion, semantic relationships, and persistent evidence. | `solomon_soss.db`, `core/solomon_knowledge_cards/` |
| **Prometheus** | Planning Engine | Auditing, plan drafting, retrieving prior failures/repairs, and bottleneck-selection. | `solomon_api/`, REST endpoints |
| **Gabriel Engine** | Skill Laboratory | Sandbox evaluation, clean-room construction, Crucible testing, and skill optimization (SS2 Quarantine). | `gabriel_engine/`, dynamic test harnesses |
| **Unified Flask Gateway** | External API | Unified API traffic routing on port 18789, dependency-injected facades, and RAG hook orchestration. | `app.py`, `backend/services/` |
| **Worker Runtime** | Background Execution | Resident daemons, Nash Swarm negotiators, and perpetual background learning loops. | `services/`, `solomon_resident_framework.py` |
| **Browser Companion** | Web Bridging | Natively configured debounced content extraction, providing bounded context to the core engine. | `solomon_browser/` |
| **Solomon API Registry** | Capability Discovery | Static inventory and metadata enforcement for all execution engines, preventing anonymous logic. | `solomon_api/engine_registry.json`, `docs/solomon_engine_registry.md` |
| **SS1/SS2/SS3 Governance** | Promotion Validation | Managing the ThreeBoxQueue, enforcing the Governance Approval Lane, and strictly gating production mutations. | `services/solomon_governance_approval_packet.py`, `governance_log.bin` |

## Ownership Rules
* **No Database Duplication:** Gabriel may not spin up its own database; all persistent state routes through Mnemosyne (the unified `solomon_soss.db`).
* **Strict Gatekeeping:** Gabriel output must pass through SS3 Governance before being considered by Prometheus or executed by Worker Runtimes.
* **Separation of Concerns:** The Flask Gateway handles the "how" of network transport, while Worker Runtimes handle the "what" of execution.
