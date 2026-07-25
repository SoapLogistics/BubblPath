import pytest
from api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_gabriel_run_loop(client):
    response = client.post("/api/v2/cognitive-core/run-loop", json={"prompt": "Test"})
    assert response.status_code == 202
    data = response.get_json()
    assert "data" in data
    assert "consensus_output" in data["data"]

def test_mnemosyne_remember(client):
    response = client.post("/api/v2/memory/remember", json={"content": "I am Jules."})
    assert response.status_code == 201
    data = response.get_json()
    assert "card_id" in data

    # Test retrieval
    response = client.get("/api/v2/memory/active-context/0")
    assert response.status_code == 200
    assert len(response.get_json()["data"]) > 0
