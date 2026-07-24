import pytest
from app import app
from solomon_50_more_step_optimizers import FiftyMoreStepOptimizers

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_50_more_step_optimizers_unit():
    report = FiftyMoreStepOptimizers.execute_all()
    assert report["status"] == "success"

    # Spot check specific LLM optimizations
    assert report["step_76"] == 7.5  # RLHF scaling
    assert report["step_82"] == 128  # HTTP3 multiplexing cap
    assert report["step_89"] == "replica" # Read replica routing
    assert report["step_109"] == (1/3)    # Jaccard
    assert report["step_125"] == 10 # OPTICS

def test_50_more_optimization_pipeline_endpoint(client):
    response = client.post("/api/command-center/optimization/ultra-deep-pipeline", json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "ultra_deep_optimization_pipeline_report" in data
    assert data["ultra_deep_optimization_pipeline_report"]["status"] == "success"
    assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]
