import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_sple_quanta_collapse(client):
    payload = {
        "task_complexity": 8.5,
        "available_nodes": 500,
        "memory_block_mb": 4096.0
    }
    response = client.post("/api/sple/quanta/collapse", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)

    # Check Routing
    assert "routing" in data
    assert "selected_node" in data["routing"]
    assert "quantum_latency_ms" in data["routing"]
    assert data["routing"]["superposition_status"] == "Collapsed"

    # Check Compression
    assert "compression" in data
    assert data["compression"]["original_size_mb"] == 4096.0
    assert data["compression"]["compressed_size_mb"] < 4096.0
    assert data["compression"]["energy_saved_joules"] > 0

def test_sple_pim_execute(client):
    payload = {
        "query_vector_size": 2048,
        "database_size_gb": 100.0
    }
    response = client.post("/api/sple/lean/pim-execute", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)

    assert data["execution_mode"] == "Processing-In-Memory (PIM)"
    assert data["bottleneck_bypassed"] is True
    assert data["pim_latency_ms"] < data["standard_von_neumann_latency_ms"]
    assert data["latency_saved_ms"] > 0
