import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_100_step_hyper_optimizer(client):
    response = client.post("/api/sple/optimize/100-step")
    assert response.status_code == 200
    data = json.loads(response.data)

    assert data["status"] == "Maximum Awesomeness Achieved"
    assert data["steps_evaluated"] == 100
    assert data["final_optimization_score"] == 100.0
    assert "execution_time_ms" in data
    assert len(data["key_highlights"]) == 8
    assert "Theoretical Physics and Autonomous Agency prioritized." in data["directive_100_status"]
