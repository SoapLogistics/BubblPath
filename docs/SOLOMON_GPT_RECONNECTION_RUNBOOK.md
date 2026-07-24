# SolomonGPT Reconnection Runbook

This guide contains instructions on how to reconnect the SolomonGPT Custom GPT interface to the real Solomon Proxy and Command Center on SS1.

---

## 1. Request Flow Path

The request path is designed as follows:

```text
SolomonGPT Custom GPT (bearer authenticated)
           ↓
Public Tunnel (Cloudflare Tunnel, Tailscale, or Reverse Proxy)
           ↓
SS1 Edge Proxy (Port 7420, solomon-proxy.js)
           ↓
Solomon API / Command Center (Port 18789, app.py)
           ↓
Mnemosyne context retrieval & Solomon Planner
```

This prevents creating dual standalone chat configurations and routes all ChatGPT/SolomonGPT interactions through a single, governed, secure endpoint.

---

## 2. Reconnecting SolomonGPT Custom GPT Actions

To configure or reconnect the SolomonGPT Custom GPT interface inside OpenAI:

1. Log into your OpenAI developer console and open your Custom GPT editor.
2. Navigate to **Configure** -> **Actions** -> **Create Action**.
3. Import the OpenAPI schema from `docs/solomon_gpt_action_openapi.yaml`.
4. Ensure the `servers.url` parameter points to your public tunnel / gateway URL.
5. Set the authentication type to **API Key**:
   - **Auth Type:** `Bearer`
   - **Token:** Paste the value of `SOLOMON_ACTIONS_API_KEY` configured in `/etc/solomon/solomon.env`.
6. Save the Action configuration.

---

## 3. Testing the Reconnection

Once configured, verify connectivity by asking SolomonGPT a direct question in the ChatGPT UI.
- Verify that the proxy logs reflect a successful `POST /api/command-center/solomon-chat` request with status `200`.
- Verify that the response includes memory metadata (`retrieved_card_ids`).
- Verify that no secrets, database files, or internal directory paths are leaked in the final response.
