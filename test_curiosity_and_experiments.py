"""
Unit and Integration Tests for SOSS Phase 2 (Curiosity Engine) and Phase 3 (Experiment Engine)
"""

import json
import pytest
from app import app, db
from solomon_curiosity_engine import PrometheusCuriosityEngine
from solomon_experiment_engine import ExperimentEngine

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestCuriosityEngine:
    """
    Tests for the Prometheus Curiosity Engine opportunity prioritizations.
    """

    def test_scoring_weights(self):
        engine = PrometheusCuriosityEngine(db)
        score = engine.calculate_lo_score(
            value=9.0,
            difficulty=5.0,
            future_use=8.0,
            risk=2.0,
            compute_cost=3.0
        )
        # Score = (0.4*9.0) + (0.2*5.0) + (0.3*8.0) - (0.2*2.0) - (0.1*3.0)
        #       = 3.6 + 1.0 + 2.4 - 0.4 - 0.3 = 6.30
        assert score == 6.30

    def test_dynamic_scan_ram_pressure(self):
        engine = PrometheusCuriosityEngine(db)

        # High RAM pressure -> scans should detect AST-PRUNE opportunities
        queue = engine.scan_for_opportunities(simulated_rss_mb=1450.0, simulated_sql_ms=0.5)
        categories = [q["category"] for q in queue]
        assert "resource_compaction" in categories

        # Low RAM pressure -> no resource_compaction opportunity
        queue_low = engine.scan_for_opportunities(simulated_rss_mb=500.0, simulated_sql_ms=0.5)
        categories_low = [q["category"] for q in queue_low]
        assert "resource_compaction" not in categories_low


class TestExperimentEngine:
    """
    Tests for the Scientific Method Pipeline.
    """

    def test_execute_experiment_promotion(self):
        exp_engine = ExperimentEngine(db)
        opportunity = {
            "name": "Audit database execution speeds",
            "category": "database_speedup"
        }
        hypothesis = "Running vacuum compresses tables and decreases latency"
        execution_script = "print('vacuum executed successfully, average speed < 1.0ms')"

        res = exp_engine.execute_reproducible_experiment(
            opportunity=opportunity,
            hypothesis=hypothesis,
            execution_script=execution_script
        )

        assert res["status"] == "success"
        pipeline = res["pipeline"]
        assert pipeline["hypothesis"]["opportunity_target"] == opportunity["name"]
        assert pipeline["evidence"]["execution_success"] is True
        assert pipeline["review"]["hypothesis_satisfied"] is True
        assert pipeline["promotion"]["status"] == "APPROVED"
        assert pipeline["promotion"]["db_persisted"] is True

        # Retrieve card from DB and verify status
        card_id = pipeline["promotion"]["card_id_promoted"]
        card = db.get_card(card_id)
        assert card["status"] == "APPROVED"
        assert "vacuum executed successfully" in card["content"]


class TestCuriosityExperimentAPIIntegration:
    """
    Verifies REST routes for curiosity queue and scientific experiment pipelines.
    """

    def test_get_curiosity_queue_endpoint(self, client):
        response = client.get("/api/command-center/curiosity/queue?simulated_rss_mb=1460.0")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["total_opportunities_found"] > 0

        # Verify it has opportunity attributes and lo_score sorted
        queue = data["learning_queue"]
        assert "lo_score" in queue[0]
        assert queue[0]["lo_score"] >= queue[-1]["lo_score"]

    def test_run_experiment_endpoint_success(self, client):
        payload = {
            "opportunity": {
                "name": "Validate learned rotations on weights",
                "category": "quantization_optimization"
            },
            "hypothesis": "Learned rotations will neutralize outlier activation limits",
            "execution_script": "print('SpinQuant rotators applied, outlier count reduced from 150 to 1')"
        }
        response = client.post("/api/command-center/curiosity/experiment", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        pipe = data["pipeline"]
        assert pipe["evidence"]["stdout"] == "SpinQuant rotators applied, outlier count reduced from 150 to 1"
        assert pipe["promotion"]["db_persisted"] is True
        assert pipe["promotion"]["status"] == "APPROVED"
