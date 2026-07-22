# SolomonGPT Runtime Map and Component Directory

This document provides a comprehensive mapping of the discovered runtime architecture, components, ports, request flows, authentication boundaries, and persistent data locations in the SS1 environment.

## 1. System Component Map & Ports

| Component | Port | Host/IP | File / Service Location | Purpose |
|---|---|---|---|---|
| **SolomonGPT** (Custom GPT) | N/A | Cloud/OpenAI | OpenAI Platform | Primary user chat interface. Initiates authenticated actions. |
| **Public Proxy / Tunnel** | HTTPS | Public DNS | `DEPLOYMENT_VERIFICATION_REQUIRED` | Exposes the SS1 proxy port (`7420`) safely to the public internet via Cloudflare Tunnel, Tailscale, or Port Forwarding. |
| **SS1 Proxy** | `7420` | `127.0.0.1` | `/srv/storage/toshiba/BubblePath/codexia-web/solomon-proxy.js` | Edge routing proxy validating `SOLOMON_ACTIONS_API_KEY` and forwarding to the Solomon API backend. |
| **Solomon API Gateway** | `18789` | `127.0.0.1` | `/home/millerm/Projects/JARVISWebUI/scripts/server/solomon_api_server.py` | Internal service exposing the Command Center API and routing requests to the Solomon planner/runtime. |
| **Project Mnemosyne Engine** | In-Process | `127.0.0.1` | `solomon_knowledge_cards/` | Thread-safe, SQL-backed long-term memory retrieval, ingestion, and governance engine. |
| **Demo / Sandbox Flask App** | `10000` | `0.0.0.0` | `app.py` | A lightweight standalone demonstration app (this repository's root entrypoint). Must NOT be confused with the production runtime. |

---

## 2. File & Process Inventory

### Known SS1 Paths
- **Solomon JS Proxy:** `/srv/storage/toshiba/BubblePath/codexia-web/solomon-proxy.js`
- **Solomon API Server (Python):** `/home/millerm/Projects/JARVISWebUI/scripts/server/solomon_api_server.py`
- **OpenClaw Workspace:** `/srv/storage/toshiba/BubblePath/openclaw-workspace`
- **Persistent Mnemosyne Database Path:** `/srv/storage/toshiba/BubblePath/data/mnemosyne/solomon_mnemosyne.db`
- **Systemd Service:** `solomon-api.service`

### Repository Layout
- `solomon_knowledge_cards/`: Reusable Python modules for Project Mnemosyne.
- `app.py`: Refactored to act as the canonical api server logic.
- `solomon-proxy.js`: Simulated Node.js proxy corresponding to `/srv/storage/toshiba/BubblePath/codexia-web/solomon-proxy.js`.
- `deploy/`: Templates and configurations for systemd, environments, and automated scripts.

---

## 3. Communication & Request Flow

The canonical, production-grade request flow for SolomonGPT is defined as:

```text
SolomonGPT (Custom GPT in ChatGPT UI)
        ↓ Authenticated HTTPS Action (Bearer Auth)
Publicly reachable proxy/tunnel (Cloudflare Tunnel, Tailscale, or reverse proxy)
        ↓
SS1 Proxy (Port 7420, solomon-proxy.js)
        ↓ Local HTTP Proxying (Validates SOLOMON_ACTIONS_API_KEY)
Solomon Actions API / Command Center API (Port 18789, solomon_api_server.py or app.py)
        ↓
Mnemosyne Context Retrieval (Prior to Planning/Answering)
        ↓ Query SQL for Approved/Active and Valid cards matching user context and clearance
Real Solomon Planner / Runtime (Core capability & LLM execution)
        ↓
Worker Execution & Tool Selection (OpenHands, Codex Carl, etc.)
        ↓
Worker Report Generation & Ingestion (idempotent, produces candidate DRAFT cards)
        ↓
SS3 Review and Promotion Gate (DRAFT -> REVIEWED -> APPROVED -> ACTIVE)
```

---

## 4. Security & Authentication Boundaries

1. **Edge Auth Verification:**
   - The SS1 Proxy validates incoming custom GPT requests by checking the `Authorization` header containing the `SOLOMON_ACTIONS_API_KEY`.
   - Constant-time string comparison (`crypto.timingSafeEqual` in Node.js, `hmac.compare_digest` in Python) is enforced.
2. **Clearance Hierarchies:**
   - Mnemosyne cards are tagged with a clearance level: `PUBLIC`, `INTERNAL`, or `RESTRICTED`.
   - Before answering, retrieval requests are bounded strictly by the caller's clearance level. For example, a `PUBLIC` request cannot retrieve `INTERNAL` or `RESTRICTED` memory cards.
3. **Draft Exclusion:**
   - No `DRAFT`, `REJECTED`, or `DEPRECATED` cards are ever loaded as trusted guidance during planning. Only `APPROVED` or `ACTIVE` cards are retrieved.

---

## 5. System Status, Identities, & Contexts

- **Solomon Identity & Soul Loading:** Loaded from the OpenClaw workspace (`/srv/storage/toshiba/BubblePath/openclaw-workspace`), containing files such as `SOUL.md`, `IDENTITY.md`, and `MEMORY.md`.
- **User Context & Tools:** Determined dynamically per task request inside the real planner.
- **Worker Report Generation:** Generated upon worker task completion. Workers serialize outcomes, which are then transmitted to `/worker-report` or processed via the `MnemosyneRuntime` adapter.
- **SS3 Reviewing Engine:** Operates as a machine-readable governance gate, transitioning candidate cards through the Review Gate.

---

## 6. Deployment Verification Status

The following details cannot be verified purely from the repository and are marked as **DEPLOYMENT_VERIFICATION_REQUIRED**:

- `DEPLOYMENT_VERIFICATION_REQUIRED`: Exact URL of the public tunnel / gateway used by SolomonGPT.
- `DEPLOYMENT_VERIFICATION_REQUIRED`: Type of public-facing tunnel in use (Cloudflare Tunnel vs. Tailscale vs. Router Forwarding).
- `DEPLOYMENT_VERIFICATION_REQUIRED`: Linux daemon users running the Node.js proxy and Python API services.
- `DEPLOYMENT_VERIFICATION_REQUIRED`: Exact production environment file location (recommended: `/etc/solomon/solomon.env` or similar).
- `DEPLOYMENT_VERIFICATION_REQUIRED`: Git branch deployed on SS1.
- `DEPLOYMENT_VERIFICATION_REQUIRED`: Credentials for SS3 reviews.
