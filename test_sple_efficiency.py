import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_route_moe_math(client):
    payload = {"query": "Calculate the Black-Scholes VaR for this portfolio."}
    response = client.post("/api/sple/efficiency/route-moe", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["selected_expert"] == "math_quant_v1"
    assert "estimated_cost_usd" in data

def test_sple_route_moe_code(client):
    payload = {"query": "Write a python def to sort this array."}
    response = client.post("/api/sple/efficiency/route-moe", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["selected_expert"] == "code_syntax_v2"

def test_sple_distill_knowledge(client):
    payload = {"source_expert": "gpt-4", "target_capability": "sentiment analysis"}
    response = client.post("/api/sple/efficiency/distill", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "distilled_sentiment_analysis" in data["new_model"]

def test_sple_roadmap_status_and_advance(client):
    # Check status
    response = client.get("/api/sple/roadmap/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["current_active_phase"] == 1

    # Advance phase
    response = client.post("/api/sple/roadmap/advance")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert data["new_phase"] == 2
