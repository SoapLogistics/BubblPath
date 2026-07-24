import pytest
import json
from app import app
from solomon_jules_bridge import JulesBridge
import os

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clean_tasks():
    if os.path.exists("jules_tasks.json"):
        os.remove("jules_tasks.json")
    yield
    if os.path.exists("jules_tasks.json"):
        os.remove("jules_tasks.json")

def test_jules_bridge_integration(client):
    res = client.post("/api/jules/task/create", json={"description": "Refactor codebase"})
    assert res.status_code == 200
    task_id = res.get_json()["task_id"]

    res = client.get("/api/jules/tasks")
    assert res.status_code == 200
    assert task_id in res.get_json()["tasks"]

    res = client.get(f"/api/jules/task/{task_id}")
    assert res.status_code == 200
    assert res.get_json()["session"]["description"] == "Refactor codebase"

    res = client.post(f"/api/jules/task/{task_id}/message", json={"message": "Commencing refactor."})
    assert res.status_code == 200

    res = client.post(f"/api/jules/task/{task_id}/validate", json={"patch_data": "diff --git..."})
    assert res.status_code == 200

    res = client.get(f"/api/jules/task/{task_id}/patch")
    assert res.status_code == 200
    assert res.get_json()["patch"] == "diff --git..."

    res = client.post(f"/api/jules/task/{task_id}/approve")
    assert res.status_code == 200

    res = client.post(f"/api/jules/task/{task_id}/cancel")
    assert res.status_code == 200

def test_browser_halt(client):
    res = client.post("/api/browser/halt")
    assert res.status_code == 200
    assert res.get_json()["status"] == "halted"
