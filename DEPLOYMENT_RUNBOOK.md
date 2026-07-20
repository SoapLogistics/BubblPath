# Project Loki & Hugin SOSS Deployment Runbook
## Production-Ready Deployment & Integration Guide

---

## 1. Overview & System Port Mapping

This runbook outlines the deployment procedure for the **Loki Sports Intelligence & Hugin Code Verification Engine (SOSS)**.
*   **Target API Service Port:** `18789` (Dynamic/configurable via `SOLOMON_API_BASE_URL`).
*   **Edge Proxy Server Port:** `7420` (Redirects to port `18789` after constant-time API key validation).
*   **Gateway Script:** `app.py`
*   **Proxy Script:** `solomon-proxy.js`

---

## 2. Infrastructure Deployment Modes

### 2.1. Render Cloud Deployment (Preferred)
Render automates deployments directly from Git repository connections.

1.  **Configure `render.yaml`:**
    The workspace configuration is defined at root:
    ```yaml
    services:
      - type: web
        name: loki-hugin-soss-gateway
        env: python
        plan: free
        buildCommand: pip install -r requirements.txt
        startCommand: python app.py
        envVars:
          - key: OPENAI_API_KEY
            sync: false
          - key: SOLOMON_ACTIONS_API_KEY
            sync: false
    ```
2.  **Web Dashboard Deployment:**
    *   Navigate to the Render Dashboard.
    *   Click **New** > **Blueprint**.
    *   Connect the branch `loki-sports-intel-blueprint-13174528251852195661`.
    *   Render will read `render.yaml`, set up the virtual environment, install Python requirements (`requirements.txt`), and spin up the gateway.

---

### 2.2. Heroku Deployment
For deployment on Heroku systems:

1.  **Login and App Creation:**
    ```bash
    heroku login
    heroku create loki-hugin-soss-gateway
    ```
2.  **Configure Environment Secrets:**
    ```bash
    heroku config:set OPENAI_API_KEY=your_openai_api_key_here
    heroku config:set SOLOMON_ACTIONS_API_KEY=your_solomon_api_key_here
    ```
3.  **Define Procfile:**
    Ensure a `Procfile` is present in the root directory:
    ```
    web: python app.py
    ```
4.  **Deploy Branch:**
    ```bash
    git push heroku loki-sports-intel-blueprint-13174528251852195661:main
    ```

---

### 2.3. Local Linux/Systemd Deployment
For deploying on a dedicated private Linux server (e.g., Ubuntu/Dell local server):

1.  **System Requirements & Setup:**
    ```bash
    sudo apt update && sudo apt install python3-pip python3-venv git -y
    cd /srv/storage/toshiba/BubblePath/
    git clone -b loki-sports-intel-blueprint-13174528251852195661 https://github.com/your-org/solomon.git loki-soss
    cd loki-soss
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configure Systemd Service (`/etc/systemd/system/loki-soss.service`):**
    ```ini
    [Unit]
    Description=Project Loki & Hugin SOSS Gateway Service
    After=network.target

    [Service]
    Type=simple
    User=jules
    WorkingDirectory=/srv/storage/toshiba/BubblePath/loki-soss
    ExecStart=/srv/storage/toshiba/BubblePath/loki-soss/venv/bin/python app.py
    Restart=always
    Environment=OPENAI_API_KEY=your_openai_api_key_here
    Environment=SOLOMON_ACTIONS_API_KEY=your_solomon_api_key_here

    [Install]
    WantedBy=multi-user.target
    ```

3.  **Enable & Start Service:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable loki-soss
    sudo systemctl start loki-soss
    sudo systemctl status loki-soss
    ```

---

## 3. Database Caches & Migrations

Project Loki and Hugin store local states and model inferences within a thread-safe SQLite transactional backend.
*   **Local DB File:** `loki_soss_cache.db`
*   **Database Initializer:** During service startup, `app.py` checks for the presence of the SQLite file and runs migration queries to create the necessary tables:
    *   `loki_projections`: Stores current player projections and lines.
    *   `loki_model_backtests`: Captures Rithmm-style historical custom backtests.
    *   `hugin_parsed_asts`: Stores parsed AST nodes and call graph structures.

To manually re-index the database cache:
```bash
python3 -c "import sqlite3; conn = sqlite3.connect('loki_soss_cache.db'); conn.execute('DROP TABLE IF EXISTS loki_projections;')"
```

---

## 4. Verification & Diagnostics

To confirm the service is operational post-deployment, run the following diagnostics:

```bash
# 1. Verify health endpoint
curl -i http://localhost:18789/api/health

# 2. Check proxy gateway routing
curl -i -H "Authorization: Bearer <SOLOMON_ACTIONS_API_KEY>" http://localhost:7420/api/command-center/status
```

---
## RECOMMENDED NEXT STEP
**Proceed with checking system integration status and verify complete repository health prior to triggering active branch commits.**
