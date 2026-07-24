import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_status(client):
    response = client.get("/api/sple/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "orchestrator_running" in data
    assert "queue_depth" in data
    assert "memory_stats" in data
    assert "optimizer_metrics" in data
    assert "swarm_nodes" in data

def test_sple_enqueue(client):
    payload = {"type": "test_task", "payload": {"data": "123"}}
    response = client.post("/api/sple/enqueue", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "Task enqueued"
    assert data["queue_depth"] > 0

def test_sple_trigger_sleep(client):
    # Enqueue a task first to put something in episodic memory
    client.post("/api/sple/enqueue", json={"type": "test", "payload": {}})

    response = client.post("/api/sple/trigger-sleep")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "consolidated_events" in data
    assert "semantic_nodes" in data

def test_sple_optimize(client):
    response = client.post("/api/sple/optimize")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "current_metrics" in data
    assert "current_hyperparameters" in data
    assert "changes_applied" in data

def test_sple_delegate(client):
    payload = {"task": "Write tests", "role": "Coder"}
    response = client.post("/api/sple/delegate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "completed"
    assert "node_id" in data
