"""
Unit and Integration Tests for SOSS Phase 22 (Model Fusion Router) and Phase 23 (Performance Predictor)
"""

import json
import pytest
from app import app, db
from solomon_model_fusion import MultiModelFusionRouter
from solomon_performance_predictor import PerformancePredictor

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestModelFusionRouter:
    """
    Tests for the Model Fusion prioritization weighting.
    """

    def test_model_fusion_constrained_vram(self):
        fusion = MultiModelFusionRouter(db)
        # Highly constrained VRAM < 2GB -> Forces quantized weights
        res = fusion.calculate_optimal_fusion_weights(
            accuracy_priority=1.0,
            latency_priority=0.0,
            vram_available_gb=1.5
        )
        assert res["status"] == "success"
        assert "CRITICAL_VRAM_CONSTRAINT" in res["allocation_reason"]
        assert res["allocated_fusion_weights"]["quantized_int4_model"] == 0.90

    def test_model_fusion_balanced_priority(self):
        fusion = MultiModelFusionRouter(db)
        res = fusion.calculate_optimal_fusion_weights(
            accuracy_priority=0.5,
            latency_priority=0.5,
            vram_available_gb=8.0
        )
        assert res["status"] == "success"
        assert "MULTI_OBJECTIVE_SOLVER" in res["allocation_reason"]
        assert res["allocated_fusion_weights"]["high_precision_target_model"] == 0.40


class TestPerformancePredictor:
    """
    Tests for the Performance Predictor heuristic solvers.
    """

    def test_predict_precision_footprints(self):
        pred = PerformancePredictor(db)

        # Test FP16 configuration
        res_fp16 = pred.predict_model_performance(model_precision="FP16", seq_len=1024)
        assert res_fp16["status"] == "success"
        assert res_fp16["predicted_metrics"]["expected_latency_ms"] == 90.0
        assert res_fp16["predicted_metrics"]["accuracy_retention_percent"] == 99.9

        # Test INT4 configuration
        res_int4 = pred.predict_model_performance(model_precision="INT4", seq_len=512)
        assert res_int4["status"] == "success"
        assert res_int4["predicted_metrics"]["expected_latency_ms"] == 12.0


class TestFusionPredictorAPIIntegration:
    """
    Verifies REST routes for Model Fusion and Performance Predictor.
    """

    def test_post_model_fusion_endpoint(self, client):
        payload = {
            "accuracy_priority": 0.80,
            "latency_priority": 0.20,
            "vram_available_gb": 12.0
        }
        response = client.post("/api/command-center/model/fusion", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "allocated_fusion_weights" in data
        assert data["allocated_fusion_weights"]["high_precision_target_model"] == 0.64

    def test_post_performance_predict_endpoint_success(self, client):
        payload = {
            "model_precision": "INT8",
            "seq_len": 2048
        }
        response = client.post("/api/command-center/performance/predict", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["predicted_metrics"]["expected_vram_gb"] > 0.0
        assert data["db_persisted_id"] == "SOK-PREDICT-PERFORMANCE-INT8"
