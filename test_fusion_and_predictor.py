"""
Unit and Integration Tests for SOSS Phase 22 and Phase 23 (Model Fusion & Performance Predictor)
"""

import json
import pytest
from app import app
from solomon_model_fusion import MultiModelFusionRouter
from solomon_performance_predictor import PerformancePredictor

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_model_fusion_routing_weights():
    profiles = [
        {"model_name": "Quantized Edge", "vram_required_gb": 4.0, "accuracy_score": 0.8},
        {"model_name": "Baseline Target", "vram_required_gb": 16.0, "accuracy_score": 0.95}
    ]

    # Under low VRAM capacity (e.g. 8GB), high vram profile matches zero weight
    res_low_vram = MultiModelFusionRouter.calculate_fusion_routing(
        available_vram_gb=8.0,
        accuracy_requirement=0.9,
        model_profiles=profiles
    )
    assert res_low_vram["optimized_fusion_weights"]["Baseline Target"] == 0.0
    assert res_low_vram["optimized_fusion_weights"]["Quantized Edge"] == 1.0

def test_model_fusion_endpoint(client):
    resp = client.post("/api/command-center/model/fusion", json={"available_vram_gb": 32.0, "accuracy_requirement": 0.95})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert "optimized_fusion_weights" in data["model_fusion_result"]

def test_performance_predictor_metrics():
    res = PerformancePredictor.predict_performance_metrics(
        num_parameters=7e9, # Llama-7B
        precision_bits=4,    # Q4 configuration
        context_tokens=1024
    )

    assert res["predicted_weight_footprint_mb"] > 0.0
    assert res["predicted_latency_per_token_ms"] > 0.0
    assert res["estimated_reasoning_quality"] > 0.0

def test_performance_predict_endpoint(client):
    payload = {
        "num_parameters": 13e9,
        "precision_bits": 8,
        "context_tokens": 512
    }
    resp = client.post("/api/command-center/performance/predict", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert "total_predicted_footprint_mb" in data["performance_prediction_result"]
