import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_expansion_holographic(client):
    payload = {"text": "A very complex high dimensional thought pattern."}
    response = client.post("/api/sple/expansion/holographic", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["phase_amplitude_encoded"] is True
    assert data["compression_ratio"] > 1.0

def test_sple_expansion_godel(client):
    # Test safe depth
    payload = {"depth": 2, "topic": "Simple math"}
    response = client.post("/api/sple/expansion/godel", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["trap_detected"] is False

    # Test unsafe recursive depth
    payload = {"depth": 10, "topic": "This statement is false"}
    response = client.post("/api/sple/expansion/godel", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["trap_detected"] is True
    assert "Paradox Exception" in data["action_taken"]

def test_sple_expansion_tda(client):
    payload = {"nodes": 1000, "edges": 10} # Very sparse, should find holes
    response = client.post("/api/sple/expansion/tda", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "structural_holes_detected" in data
    assert type(data["structural_holes_detected"]) == int

def test_sple_expansion_ou(client):
    response = client.post("/api/sple/expansion/ou-explore")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "ou_state_value" in data
    assert "exploration_action" in data

def test_sple_expansion_nash(client):
    payload = {"bid_a": 40.0, "bid_b": 60.0, "total_compute": 1000.0}
    response = client.post("/api/sple/expansion/nash-swarm", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["equilibrium_reached"] is True
    assert "agent_a_allocation" in data
    assert "agent_b_allocation" in data
