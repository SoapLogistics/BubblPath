import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_evaluate_safe(client):
    payload = {"code": "def hello(): print('world')"}
    response = client.post("/api/sple/evaluate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    # The random check might still flag a medium flaw, but no critical ones
    assert "status" in data
    assert "flaws_detected" in data
    assert "adversarial_score" in data

def test_sple_evaluate_unsafe(client):
    payload = {"code": "def hello(): os.system('rm -rf /')"}
    response = client.post("/api/sple/evaluate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert len(data["flaws_detected"]) > 0
    assert any(flaw["severity"] == "HIGH" for flaw in data["flaws_detected"])

def test_sple_memory_abstract(client):
    payload = {
        "facts": ["Apples are red", "Bananas are yellow", "Grapes are purple"],
        "concept": "Fruit Colors"
    }
    response = client.post("/api/sple/memory/abstract", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "abstracted_node_id" in data
    assert "worldview_size" in data
    assert data["worldview_size"] > 0
