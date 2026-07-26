import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.solomon_joe_bridge import JoeOmegaEngine
from backend.main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_joe_omega_engine_dry_run_default():
    engine = JoeOmegaEngine()
    response = engine.queue_blueprint("test blueprint")
    assert response["status"] == "dry-run"

def test_joe_queue_blueprint_refusal_unapproved(client):
    response = client.post('/api/joe/queue-blueprint', json={"blueprint": "test"})
    assert response.status_code == 200
    assert response.json["status"] == "dry-run"

def test_joe_queue_blueprint_approved(client):
    response = client.post('/api/joe/queue-blueprint', json={"blueprint": "test", "approved": True})
    assert response.status_code == 200
    assert response.json["status"] == "queued"
