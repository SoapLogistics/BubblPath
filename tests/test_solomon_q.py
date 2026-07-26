import pytest
import os
import json
from lab.solomon_q_engine import SolomonQEngine
from app import app

@pytest.fixture
def test_q_engine():
    filepath = "test_q_store.bin"
    if os.path.exists(filepath):
        os.remove(filepath)
    engine = SolomonQEngine(filepath=filepath, max_records=10)
    yield engine
    if os.path.exists(filepath):
        os.remove(filepath)

def test_q_engine_intake(test_q_engine):
    packet = test_q_engine.intake("test obj", "user says hi", "familyA")
    assert packet["id"] == 1
    assert packet["objective"] == "test obj"

def test_q_engine_loop(test_q_engine):
    test_q_engine.intake("test obj 1", "hi", "famA")
    test_q_engine.intake("test obj 2", "hello", "famB")

    results = test_q_engine.run_perpetual_learning_loop()
    assert len(results) == 2
    assert results[0]["id"] == 1
    assert results[0]["learning_result"] in ["lesson_written", "failure_written"]
    assert results[1]["id"] == 2

@pytest.fixture
def client(test_q_engine):
    app.config['TESTING'] = True

    # Mock get_q_engine to use our test engine
    import app as app_module
    app_module._q_engine = test_q_engine

    with app.test_client() as client:
        yield client

def test_api_q_intake(client):
    response = client.post('/api/q/intake', json={
        'objective': 'Api test',
        'user_language': 'Hi api',
        'owner_family': 'api_fam',
        'risk': 0
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data["status"] == "success"
    assert data["packet"]["objective"] == "Api test"

def test_api_q_loop(client):
    response = client.post('/api/q/loop')
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "success"
    assert type(data["processed_packets"]) == list
