# ADR 001: Reconnecting SolomonGPT and Integrating Project Mnemosyne

## Status
Approved

## Context
SolomonGPT (Custom GPT in ChatGPT) previously communicated with a standalone demo `app.py`. However, the real production Solomon environment on SS1 uses a dedicated edge Node.js proxy (`solomon-proxy.js` on port `7420`), an internal API Gateway (port `18789`), and the Project Mnemosyne Memory Card Engine. We needed to unify the codebase, prevent dual-chat-server fragmentation, and restore full secure communication paths with clearance-hierarchy enforcement and robust governance.

## Decision
1. **Unify Chat Routing:** Route all SolomonGPT requests through the unified SS1 Proxy (`solomon-proxy.js`) on port `7420`.
2. **Proxy Authentication:** Validate `SOLOMON_ACTIONS_API_KEY` using secure constant-time signature comparisons.
3. **Internal API Routing:** Forward incoming proxy traffic to the internal Flask/Python API on port `18789`.
4. **Pre-Task Mnemosyne Context Retrieval:** Before planning or generating LLM replies, query the persistent SQL-backed `MnemosyneRuntime` to retrieve only approved/active valid memory cards matching the query context and security clearance level.
5. **Worker & Review Governance:** Provide endpoints for Worker Report ingestion (producing candidate `DRAFT` cards) and SS3 Review promotions (updating lifecycles securely).
6. **Deployability & Operations:** Include fully configured systemd units, environment templates, backup/rollback deployment script, and automated live verification checklists on SS1.

## Consequences
- **Security:** Timing-attack resistant Bearer auth protects all Command Center endpoints. Clearance filters prevent information leakage across security levels.
- **Maintainability:** All schemas, models, runbooks, and tests are managed directly inside the git repository.
- **Reliability:** Automatic fallback mechanisms are implemented during DB or OpenAI failures, ensuring graceful degraded operations.
- **Robustness:** Tests cover comprehensive unit and integration behaviors, securing 100% test pass status.
