from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../gateway'))
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Bezalel Foundry Gateway"}

def test_get_mock_projects():
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert "projects" in response.json()
