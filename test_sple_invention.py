import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_invention_chronos(client):
    payload = {
        "future_state": {"AGI": True},
        "current_actions": ["Action A", "Action B", "Action C"]
    }
    response = client.post("/api/sple/invention/chronos", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)

    assert "target_future" in data
    assert "timeline_viable" in data
    assert "validated_actions" in data
    assert "pruned_actions" in data
    assert "temporal_entropy" in data
    assert type(data["temporal_entropy"]) == float

def test_sple_invention_fractal(client):
    payload = {"paradox": "The Barber of Seville paradox."}
    response = client.post("/api/sple/invention/fractal", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)

    assert "paradox" in data
    assert "previous_dimension" in data
    assert "new_dimension" in data
    assert "paradox_bypassed" in data
    assert "morph_status" in data

    # Ensure dimensionality changed (or attempted to)
    assert type(data["new_dimension"]) == float
