import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_recursive_improve(client):
    payload = {"target_module": "solomon_sple_memory"}
    response = client.post("/api/sple/recursive-improve", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)

    # Because it uses random logic, it might succeed, fail compilation, or fail benchmark.
    # We just need to assert the expected keys are present.
    assert "status" in data
    assert data["status"] in ["success", "failed", "reverted"]
    assert "generation" in data

    if data["status"] == "success":
        assert "mutation" in data
        assert "new_efficiency" in data
        assert "gain" in data
    else:
        assert "reason" in data
        assert "efficiency" in data
