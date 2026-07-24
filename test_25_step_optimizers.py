import pytest
import json
from app import app
from solomon_25_step_optimizers import TwentyFiveStepOptimizers

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_25_step_optimizers_unit():
    report = TwentyFiveStepOptimizers.execute_all()
    assert report["status"] == "success"

    # Spot check a few specific optimizations
    assert len(report["step_1"]) == 1
    assert report["step_1"][0]["id"] == 2 # 20 > 10 last accessed

    assert "B" not in report["step_2"] # Pruned orphan node B

    assert len(report["step_3"]) == 2 # Dim reduction to 2

    assert report["step_4"] == "INT8" # 12000 MB VRAM -> INT8

    assert len(report["step_13"]["content"]) <= 103 # Compacted card

    assert report["step_21"] == ["T2", "T3"] # Context sliding window

def test_optimization_pipeline_endpoint(client):
    response = client.post("/api/command-center/optimization/pipeline", json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "optimization_pipeline_report" in data
    assert data["optimization_pipeline_report"]["status"] == "success"
    assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]
