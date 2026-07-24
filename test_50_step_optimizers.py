import pytest
from app import app
from solomon_50_step_optimizers import FiftyStepOptimizers

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_50_step_optimizers_unit():
    report = FiftyStepOptimizers.execute_all()
    assert report["status"] == "success"

    # Spot check specific LLM optimizations
    assert report["step_26"] == 0.9  # Adaptive top-p
    assert report["step_30"] == 2.0  # RoPE scaling context=8192
    assert report["step_31"] is True # Flash Attention v2
    assert report["step_41"] == 2    # Radix Trie cache hit count
    assert report["step_59"] == "ZeRO-3" # DeepSpeed ZeRO 3
    assert report["step_68"] == 4.25 # Exl2 bitrate

def test_50_optimization_pipeline_endpoint(client):
    response = client.post("/api/command-center/optimization/deep-pipeline", json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "deep_optimization_pipeline_report" in data
    assert data["deep_optimization_pipeline_report"]["status"] == "success"
    assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]
