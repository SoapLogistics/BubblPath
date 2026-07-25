import pytest
from api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "service": "solomon-gateway"}

def test_not_found(client):
    response = client.get("/invalid-route")
    assert response.status_code == 404
