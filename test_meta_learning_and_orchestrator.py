"""
Unit and Integration Tests for SOSS Phase 12 (Meta-Learning) and Phase 13 (Meta-Architect)
"""

import json
import pytest
from app import app, db
from solomon_meta_learning import MetaLearningEngine
from solomon_meta_architect import MetaArchitect

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestMetaLearning:
    """
    Tests for Meta-Learning Engine algorithm self-tunings.
    """

    def test_meta_learning_defensive_risk_mitigation(self):
        engine = MetaLearningEngine(db)

        # High failure rate history
        failures_history = [
            {"success": False},
            {"success": True},
            {"success": False},
            {"success": False}
        ]
        res = engine.optimize_learning_algorithms(failures_history)
        assert res["status"] == "success"
        assert len(res["adjustments_applied"]) == 1
        assert "DEFENSIVE_RISK_MITIGATION" in res["adjustments_applied"][0]
        assert res["optimized_wisdom_weights"]["w_risks"] == 0.40


class TestMetaArchitect:
    """
    Tests for the Sovereign Meta-Architect Orchestrator.
    """

    def test_meta_architect_epoch_iteration(self):
        orchestrator = MetaArchitect(db)
        res = orchestrator.execute_autonomous_evolution_epoch()

        assert res["status"] == "success"
        assert "EPOCH-" in res["epoch_id"]
        assert res["execution_latency_ms"] > 0.0

        reconciliation = res["reconciliation"]
        assert "self_repair" in reconciliation
        assert "self_study" in reconciliation

        assert "curiosity" in res
        assert "meta_learning" in res
        assert "wisdom_gate" in res
        assert "cognitive_loop" in res
        assert "ledger_sync" in res


class TestMetaLearningOrchestratorAPIIntegration:
    """
    Verifies REST routes for Meta-Learning Optimization and Sovereign Epoch Iterations.
    """

    def test_post_meta_learning_optimize_endpoint(self, client):
        payload = {
            "execution_history": [
                {"success": True},
                {"success": True},
                {"success": True},
                {"success": True}
            ]
        }
        response = client.post("/api/command-center/meta-learning/optimize", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert len(data["adjustments_applied"]) == 1
        assert "AGGRESSIVE_DIFFICULTY_DEPRECIATION" in data["adjustments_applied"][0]
        assert data["optimized_curiosity_weights"]["w_d"] == 0.10

    def test_post_orchestrator_epoch_endpoint(self, client):
        payload = {
            "simulated_memory_mb": 1420.0,
            "simulated_sql_ms": 1.2
        }
        response = client.post("/api/command-center/orchestrator/epoch", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "epoch_id" in data
        assert data["reconciliation"]["self_repair"]["status"] == "success"
        assert data["ledger_sync"]["status"] == "success"
