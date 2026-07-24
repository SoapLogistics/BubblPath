"""
Unit and integration tests for Solomon SOSS Phase 12: Learning How to Learn (Meta-Learning) & Phase 13: SOSS Worker Foreman Orchestrator
"""

import json
import pytest
from app import app, curiosity_engine, meta_learning_engine, worker_orchestrator


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestMetaLearningEngine:
    """
    Verifies Meta-Learning rate calibration trends and dynamic curiosity weight adjustments.
    """

    def test_meta_learning_flat_progress_intensify(self):
        engine = meta_learning_engine.__class__(curiosity_engine, meta_learning_engine.experiment_engine)
        # Seed initial epoch progress
        engine.record_epoch_progress(5)  # Epoch 0: gained 5 cards
        engine.record_epoch_progress(3)  # Epoch 1: gained 3 cards (flat/decaying momentum)

        result = engine.optimize_learning_how_to_learn()
        assert result["optimized"] is True
        assert result["tuning_mode"] == "INTENSIFY_CURIOSITY"
        # Curiosity weights should have escalated to accelerate breakthroughs
        assert result["calibrated_weights"]["new_value_weight"] > result["calibrated_weights"]["old_value_weight"]

    def test_meta_learning_accelerating_progress_stabilize(self):
        engine = meta_learning_engine.__class__(curiosity_engine, meta_learning_engine.experiment_engine)
        engine.record_epoch_progress(5)  # Epoch 0: gained 5 cards
        engine.record_epoch_progress(12) # Epoch 1: gained 12 cards (exponential progress)

        result = engine.optimize_learning_how_to_learn()
        assert result["optimized"] is True
        assert result["tuning_mode"] == "STABILIZE_STEADY_STATE"


class TestWorkerForemanOrchestrator:
    """
    Verifies prefix-based query parsing and dynamic worker dispatching logic.
    """

    def test_orchestrate_gabriel_worker(self):
        res = worker_orchestrator.orchestrate_query("Gabriel: Deconstruct docker-cli")
        assert res["routed_worker"] == "Gabriel (Assimilation Engine)"
        assert "docker-cli" in res["result"]

    def test_orchestrate_mnemosyne_worker(self):
        res = worker_orchestrator.orchestrate_query("Mnemosyne: Search for quantization procedures")
        assert res["routed_worker"] == "Mnemosyne (Memory Cards OS)"
        assert "Semantic card matches" in res["result"]

    def test_orchestrate_prometheus_worker(self):
        res = worker_orchestrator.orchestrate_query("Prometheus: Map dynamic opportunities")
        assert res["routed_worker"] == "Prometheus (Curiosity Engine)"

    def test_orchestrate_loki_worker(self):
        res = worker_orchestrator.orchestrate_query("Loki: Solve moneyline edges")
        assert res["routed_worker"] == "Loki (Sports Analytical Solver)"
        assert "Sabrina Ionescu" in res["result"]

    def test_orchestrate_default_worker(self):
        res = worker_orchestrator.orchestrate_query("What is the speed of light?")
        assert res["routed_worker"] == "General Orchestrator (Google Jules Persona)"
        assert "What is the speed of light?" in res["result"]


class TestMetaLearningAndOrchestratorAPI:
    """
    Integration tests for Flask API meta-learning and orchestrator endpoints.
    """

    def test_api_meta_learning_tune(self, client):
        # We need at least 2 records to trigger tuning
        client.post("/api/mnemosyne/meta-learning/tune", data=json.dumps({"new_reusable_cards": 5}), content_type="application/json")
        res = client.post(
            "/api/mnemosyne/meta-learning/tune",
            data=json.dumps({"new_reusable_cards": 3}),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["optimized"] is True
        assert "tuning_mode" in data

    def test_api_orchestrate(self, client):
        payload = {
            "message": "Gabriel: Profile kubernetes-cli binary parameter mappings"
        }
        res = client.post(
            "/api/command-center/orchestrate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["routed_worker"] == "Gabriel (Assimilation Engine)"
        assert "action_recommended" in data
