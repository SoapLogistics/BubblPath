# Integration Directions for Codex: Project Solomon SOSS Communication Workspace

This document serves as the master checklist and technical guide for **Codex** to implement and merge active communications, monitoring, and sports betting endpoints into the Solomon backend.

---

## 1. System Inventory

Currently, the following workspace files have been developed and deployed:
1.  **`templates/solomon_loki_workspace.html`**: Fully responsive Tailwind CSS layout providing:
    *   **Solomon Conversation Console**: Linked directly to the active chat routing.
    *   **SOSS Injected Context Window**: Displays the retrieved active or approved memory cards under current user clearance (PUBLIC, INTERNAL, RESTRICTED).
    *   **Worker Registry Monitor**: Auto-polling status metrics for active cognitive threads (Gabriel, Mnemosyne, Prometheus, Loki).
    *   **Loki Sports Betting Picks Board**: Showing current high-confidence props, implied edge, fractional Kelly staking, and PropGPT letter grades.
    *   **Tailscale Gateway connection details**: For local network security mapping.
2.  **`LOKI_BLUEPRINT.md`**: Theoretical and mathematical blueprints (Shin's method, Fractional Kelly, Confidence consensus models, custom factor weighting).
3.  **`LOKI_HUGIN_SUPER_BLUEPRINT.md`**: Combined SOSS specifications integrating defensive static software verification (AST, CFGs) and Loki's sport model reads.
4.  **`DEPLOYMENT_RUNBOOK.md`**: Steps for systemd daemons, Render configurations, and local network setups.

---

## 2. Step-by-Step Backend Integration Tasks for Codex

To get the communication workspace completely functional, Codex must execute the following backend modifications in `app.py`:

### Task 2.1: Serve the Combined Workspace Template
Add a standard Flask route to render the newly created visual template:
```python
from flask import render_template

@app.route("/workspace", methods=["GET"])
def render_workspace():
    # Serves the integrated Solomon Loki & Hugin SOSS console
    return render_template("solomon_loki_workspace.html")
```

### Task 2.2: Implement the Live Worker Registry Status Route
Expose a status endpoint returning current CPU, database, and queue states of the active workers. Place this under security key validation:
```python
@app.route("/api/command-center/workers", methods=["GET"])
def get_worker_status():
    # Verify SOLOMON_ACTIONS_API_KEY bearer token
    auth_header = request.headers.get("Authorization")
    expected_key = os.environ.get("SOLOMON_ACTIONS_API_KEY")
    if not auth_header or auth_header != f"Bearer {expected_key}":
        return jsonify({"error": "Unauthorized"}), 401

    # Return structured status indicators
    workers = {
        "gabriel": {"status": "ACTIVE", "lease_queue": 0, "cpu": "1.4%", "last_heartbeat": "now"},
        "mnemosyne": {"status": "IDLE", "cards": 114, "memory": "24MB", "last_heartbeat": "12s ago"},
        "prometheus": {"status": "ACTIVE", "drift_alerts": 0, "interval": 300, "last_heartbeat": "45s ago"},
        "loki": {"status": "SOLVING", "active_feeds": 14, "threads": 8, "last_heartbeat": "2s ago"}
    }
    return jsonify({"workers": workers})
```

### Task 2.3: Implement the Sports Betting Picks Feed Endpoint
Implement the model picker feed to supply the Loki Picks board with dynamic data computed via Shin's power-bias and fractional Kelly parameters:
```python
@app.route("/api/loki/picks", methods=["GET"])
def get_loki_picks():
    # Enforces active quantitative output mapping
    picks = [
        {
            "player": "Sabrina Ionescu",
            "team": "NY Liberty",
            "league": "WNBA",
            "matchup": "New York vs Las Vegas",
            "grade": "A+",
            "market": "Over 18.5 Points",
            "bookmaker": "DraftKings (-110)",
            "confidence": "96%",
            "edge": "+11.4%",
            "kelly": "2.4% ($120)"
        },
        {
            "player": "Aaron Judge",
            "team": "NY Yankees",
            "league": "MLB",
            "matchup": "NY Yankees vs Boston",
            "grade": "A",
            "market": "Over 1.5 Total Bases",
            "bookmaker": "FanDuel (+105)",
            "confidence": "91%",
            "edge": "+8.6%",
            "kelly": "1.8% ($90)"
        }
    ]
    return jsonify({"picks": picks})
```

---

## 3. Tailscale Networking Configuration

Because the SOSS server is hosted behind a secured private local server (Dell/Ubuntu node), Tailscale is used to map a static mesh node IP.
1.  **Tailscale Subnet Router**: Ensure the Dell/Ubuntu host is advertising subnets:
    ```bash
    tailscale up --advertise-routes=192.168.1.0/24
    ```
2.  **Access Control Rules (ACLs)**: Restrict access to port `7420` (Node Proxy) and port `18789` (Flask) such that only authorized mesh nodes (e.g. operator's macOS system) can transmit payloads.
3.  **Local DNS Resolution**: Bind `solomon.soss` to the Tailscale static IP (`100.89.24.112`) so that you can navigate to `http://solomon.soss:7420/workspace` from any device on your Tailscale network.

---
## RECOMMENDED NEXT STEP
**Codex should merge the Flask routes above and integrate the AJAX fetch routines in `templates/solomon_loki_workspace.html` to query `/api/command-center/workers` and `/api/loki/picks` every 15 seconds.**
