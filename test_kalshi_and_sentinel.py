"""
Unit and Integration Tests for SOSS Phase 16 and Phase 17 (Kalshi Prediction & System Sentinel)
"""

import json
import pytest
from app import app
from solomon_kalshi_predictor import KalshiPredictor
from solomon_system_sentinel import SystemSentinel

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_kalshi_predictor_kelly_formula():
    # Test safe prediction wager estimation
    res = KalshiPredictor.calculate_kelly_stake(
        market_price_cents=60.0, # 60c contract
        model_probability=0.7,   # 70% model probability
        bankroll=500.0,
        fractional_multiplier=0.5
    )

    assert res["allocation_action"] == "BUY"
    assert res["raw_kelly_fraction"] > 0.0
    assert res["suggested_wager"] > 0.0

def test_kalshi_predictor_endpoint(client):
    payload = {
        "market_price_cents": 40.0,
        "model_probability": 0.8,
        "bankroll": 1000.0
    }
    resp = client.post("/api/command-center/kalshi/simulate", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert "suggested_wager" in data["kalshi_simulation_result"]

def test_sentinel_ast_verification():
    res = SystemSentinel.audit_file_syntax("solomon_system_sentinel.py")
    assert res["syntactically_valid"] is True
    assert res["classes_count"] == 1
    assert res["functions_count"] == 1

def test_sentinel_endpoint(client):
    resp = client.post("/api/command-center/sentinel/verify", json={"filepath": "solomon_system_sentinel.py"})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert data["sentinel_verification_result"]["syntactically_valid"] is True
