import pytest
from app import app
import json
from solomon_context_budgeter import DynamicContextBudgeter

def test_dynamic_context_budgeter():
    budgeter = DynamicContextBudgeter()
    history = [
        {"content": "short string"},
        {"content": "A much longer string that takes up more space", "semantic_score": 0.9}
    ]

    # Large memory
    res = budgeter.evaluate_budget(1000, 1000, history)
    assert res['dynamic_char_limit'] == 10000
    assert len(res['pruned_history']) == 2

    # Very small memory
    res2 = budgeter.evaluate_budget(10, 10, history)
    assert res2['dynamic_char_limit'] == 500  # min limit
    assert len(res2['pruned_history']) == 2

def test_dynamic_context_budgeter_pruning():
    budgeter = DynamicContextBudgeter()
    history = []
    for i in range(10):
        history.append({"content": "A" * 100, "semantic_score": i * 0.1})

    res = budgeter.evaluate_budget(50, 50, history)
    # limit = 500 chars. Should only keep 5 items.
    assert res['dynamic_char_limit'] == 500
    assert len(res['pruned_history']) == 5

    # Make sure we kept the highest score items (plus recency boost)
    # The last items have higher score AND higher recency, so they should be kept
    # original indices kept: 5,6,7,8,9
    assert res['pruned_history'][0]['semantic_score'] == 0.5
    assert res['pruned_history'][4]['semantic_score'] == 0.9

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_endpoint_context_budget(client):
    payload = {
        "available_ram_mb": 50,
        "available_vram_mb": 50,
        "prompt_history": [{"content": "A" * 100, "semantic_score": 0.5} for _ in range(10)]
    }
    resp = client.post("/api/command-center/context/budget", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert data["budget_report"]["pruned_history_count"] == 5
