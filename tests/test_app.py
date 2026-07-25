import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['AUTH_KEY'] = 'test_key'
    with app.test_client() as client:
        yield client

def test_health_check(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert b'healthy' in rv.data

def test_chat_unauthorized(client):
    rv = client.post('/chat', json={"message": "hello"})
    assert rv.status_code == 401

def test_chat_authorized_empty(client):
    rv = client.post('/chat', headers={"Authorization": "Bearer test_key"}, json={"message": ""})
    assert rv.status_code == 400
    assert b'cannot be empty' in rv.data
