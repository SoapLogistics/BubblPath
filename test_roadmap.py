import json
import pytest
from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_worker_modes_endpoint(client):
    """
    Test GET and POST on /api/command-center/worker-modes.
    """
    # 1. GET
    res_get = client.get("/api/command-center/worker-modes")
    assert res_get.status_code == 200
    data_get = json.loads(res_get.data)
    assert data_get["status"] == "success"
    assert "worker_modes" in data_get
    assert "Gabriel" in data_get["worker_modes"]

    # 2. POST (valid update)
    res_post = client.post("/api/command-center/worker-modes", json={
        "worker_id": "Gabriel",
        "mode": "READ_WRITE"
    })
    assert res_post.status_code == 200
    data_post = json.loads(res_post.data)
    assert data_post["status"] == "success"
    assert "promoted" in data_post["message"]

    # Verify update
    res_verify = client.get("/api/command-center/worker-modes")
    data_verify = json.loads(res_verify.data)
    assert data_verify["worker_modes"]["Gabriel"] == "READ_WRITE"

    # 3. POST (invalid validation check)
    res_invalid_worker = client.post("/api/command-center/worker-modes", json={
        "worker_id": "UnknownWorker",
        "mode": "LIVE"
    })
    assert res_invalid_worker.status_code == 400


def test_concurrency_load_testing_endpoint(client):
    """
    Test POST on /api/command-center/load-test.
    """
    res = client.post("/api/command-center/load-test", json={
        "requests_count": 10,
        "concurrency_level": 5,
        "query": "Hessian trace dynamic allocation VRAM"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["total_requests_executed"] == 10
    assert data["concurrency_level"] == 5
    assert data["successful_requests"] == 10
    assert data["failed_requests"] == 0
    assert data["thread_safety_status"] == "GUARANTEED / SAFELY LOCKED"


def test_context_budget_simulation_endpoint(client):
    """
    Test POST on /api/command-center/context/budget-simulation under high RAM pressure.
    """
    history = [
        "Prompt message 1: Initialize model loaders",
        "Prompt message 2: Compile local calibration datasets",
        "Prompt message 3: Apply SpinQuant learned rotations on model weights",
        "Prompt message 4: Verify ethical boundaries with wisdom layer"
    ]

    # Moderate RAM pressure
    res_moderate = client.post("/api/command-center/context/budget-simulation", json={
        "prompt_history": history,
        "simulated_rss_mb": 1100.0
    })
    assert res_moderate.status_code == 200
    data_mod = json.loads(res_moderate.data)
    assert data_mod["status"] == "success"
    assert data_mod["pruning_mode"] == "MODERATE"
    assert data_mod["compressed_1bit_activated"] is False

    # Critical RAM pressure (approaching 1.5GB cap)
    res_critical = client.post("/api/command-center/context/budget-simulation", json={
        "prompt_history": history,
        "simulated_rss_mb": 1450.0
    })
    assert res_critical.status_code == 200
    data_crit = json.loads(res_critical.data)
    assert data_crit["status"] == "success"
    assert data_crit["pruning_mode"] == "CRITICAL_PRUNING"
    assert data_crit["compressed_1bit_activated"] is True
    assert "16:1" in data_crit["semantic_compression_ratio"]


def test_loki_calibrate_endpoint(client):
    """
    Test POST on /api/command-center/loki/calibrate (Shin/Kelly solver with relational weights).
    """
    # Seed a target SOK card to match event_query semantic boost
    db.upsert_card(
        card_id="SOK-LOKI-TEST",
        family="Task",
        focus="Loki sports betting prediction metrics",
        content="Optimize Shin probability solver configurations for live calibrations."
    )

    res = client.post("/api/command-center/loki/calibrate", json={
        "bookmaker_odds": [1.85, 2.15],
        "bankroll": 5000.0,
        "event_query": "Loki sports betting prediction metrics"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["mock_event_feed_synchronized"] is True
    assert data["overround_detected"] > 0.0
    assert "sok_card_calibration" in data
    assert data["sok_card_calibration"]["matched_card_id"].startswith("SOK-")
    assert "kelly_criterion_output" in data
    assert "recommended_cash_wagers" in data["kelly_criterion_output"]


def test_extension_sync_endpoint(client):
    """
    Test POST on /api/mnemosyne/extension-loop/sync (MV3 side-panel traces with anti-XSS).
    """
    res = client.post("/api/mnemosyne/extension-loop/sync", json={
        "tab_id": "tab_loki_99",
        "dom_content": "<div class='panel'>Unbelievable sports bets calibrated!</div>",
        "feature": "Sports_Betting_Monitor"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["tab_id_synced"] == "tab_loki_99"
    assert data["new_card_registered"] == "SOK-SYNC-MV3-tab_loki_99"
    # Ensure raw HTML is sanitized / escaped
    assert "&lt;div" in data["sync_trace_details"]["preview"]
