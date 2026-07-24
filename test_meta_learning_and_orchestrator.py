"""
Unit and Integration Tests for SOSS Phase 13 (Worker Foreman Orchestrator)
"""

import json
import pytest
from app import app, db
from solomon_orchestrator import WorkerForemanOrchestrator

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_orchestrator_unit_routing():
    orch = WorkerForemanOrchestrator()

    # Test prefix-based routing logic
    res_gabriel = orch.delegate_message("Gabriel: Run security audit on AST files.")
    assert res_gabriel["routing_status"] == "DELEGATED"
    assert "Gabriel" in res_gabriel["target_worker"]

    res_loki = orch.delegate_message("Loki: Calculate optimal fractional stake.")
    assert res_loki["routing_status"] == "DELEGATED"
    assert "Loki" in res_loki["target_worker"]

    res_standard = orch.delegate_message("Standard query for general information.")
    assert res_standard["routing_status"] == "STANDARD_ROUTED"

def test_orchestrator_integration_endpoint(client):
    payload = {"message": "Prometheus: Discover database confidence gaps."}
    resp = client.post("/api/command-center/orchestrator/delegate", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert "Prometheus" in data["delegation_result"]["target_worker"]
