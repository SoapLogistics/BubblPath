"""
Unit and integration tests for Solomon SOSS Phase 6: Learning Process Optimization (Self-Study)
"""

import json
import pytest
from app import app, study_optimizer


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSelfStudyOptimizer:
    """
    Verifies Self-Study metrics analysis, threshold adjustments, and API routing.
    """

    def test_optimization_success_relax(self):
        optimizer = study_optimizer.__class__(initial_search_threshold=0.20)
        optimizer.record_search_telemetry(0.50, 0.90) # high success
        optimizer.record_search_telemetry(0.60, 0.95)

        result = optimizer.execute_self_study_optimization()
        assert result["tuned"] is True
        assert result["tuning_action"] == "RELAXED_EXPLORATION"
        assert result["parameters"]["new_search_threshold"] < 0.20

    def test_optimization_failure_tighten(self):
        optimizer = study_optimizer.__class__(initial_search_threshold=0.20)
        optimizer.record_search_telemetry(0.20, 0.40) # low success

        result = optimizer.execute_self_study_optimization()
        assert result["tuned"] is True
        assert result["tuning_action"] == "TIGHTENED_SECURITY_GATING"
        assert result["parameters"]["new_search_threshold"] > 0.20


class TestSelfStudyAPI:
    """
    Integration tests for Flask API study optimization routes.
    """

    def test_api_study_optimize_workflow(self, client):
        payload = {
            "avg_cosine_similarity": 0.45,
            "user_feedback_success_rate": 0.88
        }
        res = client.post(
            "/api/mnemosyne/study/optimize",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["tuned"] is True
        assert "tuning_action" in data
        assert "parameters" in data
