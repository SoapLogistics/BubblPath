"""
Unit and Integration Tests for SOSS Phase 20 (Dynamic Context Budgeter) and Phase 21 (RAG Vector Compressor)
"""

import json
import pytest
from app import app, db
from solomon_context_budgeter import DynamicContextBudgeter
from solomon_vector_compressor import RAGVectorCompressor

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestDynamicContextBudgeter:
    """
    Tests for the Dynamic Context Budgeter memory-adaptive pruning.
    """

    def test_context_budget_limits_by_ram(self):
        budgeter = DynamicContextBudgeter(db)

        assert budgeter.calculate_optimal_context_limit(1200.0) == 16000
        assert budgeter.calculate_optimal_context_limit(750.0) == 8000
        assert budgeter.calculate_optimal_context_limit(300.0) == 2000

    def test_context_allocation_pruning(self):
        budgeter = DynamicContextBudgeter(db)
        history = [
            {"role": "system", "content": "Directives"},
            {"role": "user", "content": "A" * 1500},
            {"role": "assistant", "content": "B" * 1000}
        ]

        # limit is 2000 characters. Keep system prompt, and keepassistant response (1000 Chars).
        # user response (1500 Chars) is pruned since 1500 + 1000 + 10 > 2000 limit.
        res = budgeter.optimize_context_allocation(history, available_ram_mb=300.0)
        assert res["status"] == "success"
        assert res["allocated_limit_chars"] == 2000
        assert len(res["pruned_history"]) == 2
        assert res["pruned_history"][0]["role"] == "system"
        assert res["pruned_history"][1]["role"] == "assistant"


class TestRAGVectorCompressor:
    """
    Tests for the 1-bit sign RAG Vector Compressor.
    """

    def test_vector_binarization_similarity(self):
        compressor = RAGVectorCompressor(db)

        original = [0.1, -0.4, 0.5, -0.9]
        compressed = compressor.compress_vector_representation(original)

        # Compressed should be [1.0, -1.0, 1.0, -1.0]
        assert compressed == [1.0, -1.0, 1.0, -1.0]

        similarity = compressor.compute_compressed_cosine_similarity(original, compressed)
        assert similarity > 0.0
        assert -1.0 <= similarity <= 1.0


class TestBudgetCompressorAPIIntegration:
    """
    Verifies REST routes for Context Budgeter and Vector Compressor.
    """

    def test_post_context_budget_endpoint(self, client):
        payload = {
            "prompt_history": [
                {"role": "system", "content": "Task constraints"},
                {"role": "user", "content": "Hello world conversation context"}
            ],
            "available_ram_mb": 400.0
        }
        response = client.post("/api/command-center/context/budget", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["allocated_limit_chars"] == 2000
        assert data["allocated_elements_count"] == 2

    def test_post_vector_compress_endpoint_success(self, client):
        payload = {
            "card_id": "SOK-MISSION-QUANT-001"
        }
        response = client.post("/api/command-center/vector/compress", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["card_id_processed"] == "SOK-MISSION-QUANT-001"
        assert data["original_dimension"] == 128
        assert data["reconstruction_similarity"] > 0.0
