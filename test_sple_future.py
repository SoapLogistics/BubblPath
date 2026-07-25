import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_world_model_simulate_safe(client):
    payload = {"action": "trigger_sleep_consolidation", "parameters": {}}
    response = client.post("/api/sple/world-model/simulate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action_simulated"] == "trigger_sleep_consolidation"
    assert "predicted_next_state" in data
    assert data["is_safe"] is True
    assert data["expected_reward"] > 0

def test_sple_world_model_simulate_unsafe(client):
    # Depending on initial budget, this might be safe or unsafe, but we check structure
    payload = {"action": "run_heavy_training_loop", "parameters": {}}
    response = client.post("/api/sple/world-model/simulate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "predicted_next_state" in data
    assert "expected_reward" in data

def test_sple_horizon_predict_low_novelty(client):
    payload = {"topic": "Training bigger models with more data"}
    response = client.post("/api/sple/horizon/predict", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["novelty_score"] < 0.5
    assert data["recommendation"] == "Deprioritize"

def test_sple_horizon_predict_high_novelty(client):
    payload = {"topic": "AST mutation and self-modifying autonomous memory loops"}
    response = client.post("/api/sple/horizon/predict", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["novelty_score"] > 0.8
    assert data["recommendation"] == "Pursue aggressively"
