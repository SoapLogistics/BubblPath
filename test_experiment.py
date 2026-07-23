"""
Integration and unit tests for Solomon SOSS Phase 3: Experiment Engine (Scientific Method Pipeline)
"""

import json
import pytest
from app import app, db, curiosity_engine, experiment_engine
from solomon_curiosity_engine import LearningOpportunity
from solomon_experiment_engine import ExperimentEngine


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestExperimentEngine:
    """
    Verifies Experiment formulation, sandbox executions, and promotions to Mnemosyne.
    """

    def test_formulate_and_execute_standard(self):
        lo = LearningOpportunity(
            task_id="EXP-UNIT-1",
            title="Optimizing Embeddings",
            description="Test custom embedding models.",
            value=7.0,
            difficulty=5.0,
            future_use=8.0,
            risk=2.0,
            compute_cost=1.5,
            is_absurd=False
        )
        ee = ExperimentEngine(db)
        experiment = ee.formulate_experiment(lo)

        assert experiment.experiment_id.startswith("EXP-EXP-UNIT-1-")
        assert "Standard Hypothesis" in experiment.hypothesis
        assert len(experiment.plan) == 4
        assert experiment.status == "PLANNED"

        # Execute sandbox
        evidence = ee.execute_sandbox_experiment(experiment.experiment_id)
        assert experiment.status == "REVIEWED"
        assert experiment.execution_success is True
        assert "Successfully verified code repair" in evidence["stdout_log"]
        assert evidence["latency_ms"] > 0.0

        # Promote
        success, msg = ee.promote_to_mnemosyne(experiment.experiment_id)
        assert success is True
        assert "Successfully promoted" in msg
        assert experiment.status == "PROMOTED"

        # Check that card exists in the DB
        card = db.get_card("SOK-KNOWLEDGE-EXP-UNIT-1")
        assert card is not None
        assert card["focus"] == f"Empirical proof from {experiment.experiment_id}"

    def test_formulate_and_execute_absurd(self):
        lo = LearningOpportunity(
            task_id="EXP-UNIT-ABSURD",
            title="Absurd Quantizer",
            description="Ternary weights optimization.",
            value=8.0,
            difficulty=9.0,
            future_use=9.0,
            risk=8.0,
            compute_cost=5.0,
            is_absurd=True
        )
        ee = ExperimentEngine(db)
        experiment = ee.formulate_experiment(lo)

        assert "Absurd Hypothesis" in experiment.hypothesis

        # Execute custom sandbox action
        def custom_action():
            return "Custom binary verification succeeded.", True

        evidence = ee.execute_sandbox_experiment(experiment.experiment_id, custom_action)
        assert experiment.execution_success is True
        assert evidence["stdout_log"] == "Custom binary verification succeeded."


class TestCuriosityAndExperimentAPI:
    """
    Integration tests for Flask API routes managing Curiosity queue and Experiment pipeline.
    """

    def test_api_curiosity_workflow(self, client):
        # 1. Get queue
        res = client.get("/api/curiosity/queue")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"

        # 2. Add an opportunity
        payload = {
            "task_id": "API-TEST-GAP",
            "title": "API Embedding Speedup",
            "description": "Cache embeddings to memory.",
            "value": 8.0,
            "difficulty": 4.0,
            "future_use": 9.0,
            "risk": 1.0,
            "compute_cost": 1.0,
            "is_absurd": False
        }
        res_add = client.post(
            "/api/curiosity/add",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res_add.status_code == 200
        data_add = res_add.get_json()
        assert data_add["status"] == "success"
        assert data_add["opportunity"]["task_id"] == "API-TEST-GAP"

        # 3. Next recommendation
        res_next = client.get("/api/curiosity/next")
        assert res_next.status_code == 200
        data_next = res_next.get_json()
        assert data_next["status"] == "success"
        assert "recommended_next_step" in data_next

        # 4. Run experiment pipeline
        res_run = client.post(
            "/api/experiment/run",
            data=json.dumps({"task_id": "API-TEST-GAP"}),
            content_type="application/json"
        )
        assert res_run.status_code == 200
        data_run = res_run.get_json()
        assert data_run["status"] == "success"
        assert data_run["experiment"]["execution_success"] is True
        assert "Successfully promoted card" in data_run["message"]
