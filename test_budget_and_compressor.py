"""
Unit and Integration Tests for SOSS Phase 20 and Phase 21 (Context Budgeting & Vector Compression)
"""

import json
import pytest
from app import app
from solomon_context_budgeter import DynamicContextBudgeter
from solomon_vector_compressor import RAGVectorCompressor

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_context_budgeter_logic():
    history = [
        {"role": "user", "content": "Hello. How are you?"},
        {"role": "assistant", "content": "I am operating optimally under memory budgets."},
        {"role": "user", "content": "Run deep static security audit now."}
    ]

    # Test safe budget limits
    res_safe = DynamicContextBudgeter.budget_context(history, max_context_chars=1000, system_ram_mb=800.0)
    assert res_safe["pruned_messages_count"] == 3
    assert res_safe["ram_warning_triggered"] is False

    # Test warning limit constraints (RAM exceeded drops limits)
    res_restricted = DynamicContextBudgeter.budget_context(history, max_context_chars=50, system_ram_mb=1400.0)
    assert res_restricted["pruned_messages_count"] < 3
    assert res_restricted["ram_warning_triggered"] is True

def test_context_budget_endpoint(client):
    payload = {
        "history": [{"role": "user", "content": "test message content"}],
        "max_context_chars": 500,
        "system_ram_mb": 900.0
    }
    resp = client.post("/api/command-center/context/budget", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"

def test_vector_compressor_logic():
    float_vector = [0.45, -0.12, 0.89, -0.67]
    compressed = RAGVectorCompressor.compress_vector(float_vector)
    assert compressed == [1, 0, 1, 0]

    # Hamming distance similarity
    sim = RAGVectorCompressor.calculate_hamming_similarity([1, 0, 1, 0], [1, 1, 1, 0])
    assert sim == 0.75

def test_vector_compression_endpoint(client):
    payload = {"embeddings": [[0.1, -0.5, 0.9], [-0.3, 0.4, -0.1]]}
    resp = client.post("/api/command-center/vector/compress", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert "vector_compression_result" in data
