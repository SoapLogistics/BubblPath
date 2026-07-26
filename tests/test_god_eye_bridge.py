import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_god_eye_graph_endpoint(client):
    response = client.get('/api/memory/graph.json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'nodes' in data
    assert 'edges' in data
