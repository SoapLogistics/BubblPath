"""
Unit and Integration Tests for SOSS Phase 16 (Kalshi Predictor) and Phase 17 (System Sentinel)
"""

import json
import pytest
from app import app, db
from solomon_kalshi_predictor import KalshiPredictor
from solomon_system_sentinel import SystemSentinel

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestKalshiPredictor:
    """
    Tests for prediction market active wagers.
    """

    def test_wager_no_edge(self):
        pred = KalshiPredictor(db)
        res = pred.simulate_prediction_wager(
            market_id="test_no_edge",
            question="Will it rain tomorrow?",
            yes_price_cents=60.0,
            true_probability=0.50 # True prob < Implied Yes price -> No edge
        )
        assert res["status"] == "success"
        assert res["action"] == "PASS_NO_EDGE"
        assert res["optimal_stake"] == 0.0

    def test_wager_yes_edge(self):
        pred = KalshiPredictor(db)
        res = pred.simulate_prediction_wager(
            market_id="test_yes_edge",
            question="Will it rain tomorrow?",
            yes_price_cents=40.0,
            true_probability=0.60 # True prob > Implied Yes price -> Edge!
        )
        assert res["status"] == "success"
        assert res["action"] == "PLACE_YES_WAGER"
        assert res["optimal_stake"] > 0.0


class TestSystemSentinel:
    """
    Tests for health watchdog and compliance sentinel sweeps.
    """

    def test_sentinel_scan_stability(self):
        sent = SystemSentinel()
        res = sent.run_complete_compliance_sweep()
        assert res["status"] == "success"
        assert res["overall_health_rating"] == "STABLE"
        assert res["total_python_files_scanned"] > 0
        assert len(res["syntax_failures"]) == 0


class TestKalshiSentinelAPIIntegration:
    """
    Verifies REST routes for Kalshi simulations and Sentinel sweeps.
    """

    def test_post_kalshi_simulate_endpoint(self, client):
        payload = {
            "market_id": "STABLECOIN-VOLUME-2026",
            "question": "Will stablecoin volume exceed $1T in Dec?",
            "yes_price_cents": 55.0,
            "true_probability": 0.72,
            "bankroll_balance": 5000.0
        }
        response = client.post("/api/command-center/kalshi/simulate", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["action"] == "PLACE_YES_WAGER"
        assert data["optimal_stake"] > 0.0

    def test_post_sentinel_verify_endpoint(self, client):
        response = client.post("/api/command-center/sentinel/verify")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["overall_health_rating"] == "STABLE"
        assert data["total_python_files_scanned"] > 0
