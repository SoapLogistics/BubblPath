"""
Unit and Integration Tests for Solomon Mnemosyne SQLite DB & Semantic Search Engine.
"""

import os
import json
import pytest
from app import app
from solomon_mnemosyne_db import SolomonMnemosyneDB

@pytest.fixture
def test_db():
    db_path = "test_solomon_mnemosyne_temp.db"
    # Remove existing temp db if any
    if os.path.exists(db_path):
        os.remove(db_path)

    db = SolomonMnemosyneDB(db_path)
    yield db

    # Clean up after tests
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSolomonMnemosyneDB:
    """
    Tests for the SQLite relational card database, L2 normalized hashing embeddings,
    and cosine similarity searches with zero-division protections.
    """

    def test_database_initialization(self, test_db):
        assert os.path.exists(test_db.db_path)

        # Check initial cards retrieval (should be empty)
        cards = test_db.get_all_cards()
        assert len(cards) == 0

    def test_compute_local_embedding_l2_normalization(self, test_db):
        text = "Maintain ultra-efficient local memory footprint for edge execution."
        vector = test_db.compute_local_embedding(text)

        assert len(vector) == 128
        # Assert L2 normalized vector norm = 1.0 (approximately)
        sq_sum = sum(x ** 2 for x in vector)
        assert abs(sq_sum - 1.0) < 1e-5

    def test_compute_local_embedding_empty_text_protection(self, test_db):
        # Empty text input should return a valid normalized fallback vector without failing
        vector = test_db.compute_local_embedding("")
        assert len(vector) == 128
        sq_sum = sum(x ** 2 for x in vector)
        assert abs(sq_sum - 1.0) < 1e-5

    def test_upsert_and_retrieve_card(self, test_db):
        card_id = "SOK-TEST-CARD-999"
        family = "Mission"
        focus = "VRAM metrics"
        content = "Formulate average Hessian trace spectrums."

        assert test_db.upsert_card(card_id, family, focus, content) is True

        card = test_db.get_card(card_id)
        assert card is not None
        assert card["card_id"] == card_id
        assert card["family"] == family
        assert card["focus"] == focus
        assert card["content"] == content
        assert len(card["embedding"]) == 128
        assert card["confidence"] == 1.0

    def test_relational_directed_links(self, test_db):
        # Insert two cards
        assert test_db.upsert_card("CARD-A", "Mission", "A", "Base mission statement") is True
        assert test_db.upsert_card("CARD-B", "Procedure", "B", "Procedural step details") is True

        # Add directed link
        assert test_db.add_link("CARD-B", "CARD-A", "DEPENDS_ON") is True

        # Retrieve card to assert relationships are linked correctly
        card_b = test_db.get_card("CARD-B")
        assert len(card_b["outgoing_links"]) == 1
        assert card_b["outgoing_links"][0]["target_id"] == "CARD-A"
        assert card_b["outgoing_links"][0]["relationship_type"] == "DEPENDS_ON"

        card_a = test_db.get_card("CARD-A")
        assert len(card_a["incoming_links"]) == 1
        assert card_a["incoming_links"][0]["source_id"] == "CARD-B"
        assert card_a["incoming_links"][0]["relationship_type"] == "DEPENDS_ON"

    def test_semantic_search_cosine_similarity(self, test_db):
        # Insert diverse cards
        test_db.upsert_card("CARD-RAM", "Procedure", "RAM", "Configure VRAM limits and memory budget knapsack constraints.")
        test_db.upsert_card("CARD-WEATHER", "Procedure", "Weather", "Forecast atmospheric pressure and temperature precipitation.")

        # Search for RAM concepts
        results_ram = test_db.semantic_search("knapsack VRAM memory", top_k=5)
        assert len(results_ram) == 2
        # First result should be the RAM card with higher similarity score
        assert results_ram[0]["card_id"] == "CARD-RAM"
        assert results_ram[1]["card_id"] == "CARD-WEATHER"
        assert results_ram[0]["similarity"] > results_ram[1]["similarity"]

        # Assert capped boundary conditions
        for r in results_ram:
            assert -1.0 <= r["similarity"] <= 1.0

    def test_card_confidence_scaling(self, test_db):
        card_id = "SOK-TEST-CONF"
        test_db.upsert_card(card_id, "Procedure", "Test", "Testing confidence scaling loops.")

        # Success upgrade
        success, conf1 = test_db.update_card_confidence(card_id, "success", learning_rate=0.05)
        assert success is True
        assert conf1 == 1.05

        # Success upgrade again
        _, conf2 = test_db.update_card_confidence(card_id, "success", learning_rate=0.05)
        assert conf2 == 1.1025

        # Failure downgrade
        _, conf3 = test_db.update_card_confidence(card_id, "failure", learning_rate=0.10)
        assert abs(conf3 - (1.1025 * 0.90)) < 1e-4

        # Verify clipping upper bound [2.0]
        for _ in range(50):
            test_db.update_card_confidence(card_id, "success", learning_rate=0.20)
        card = test_db.get_card(card_id)
        assert card["confidence"] == 2.0

        # Verify clipping lower bound [0.1]
        for _ in range(50):
            test_db.update_card_confidence(card_id, "failure", learning_rate=0.20)
        card = test_db.get_card(card_id)
        assert card["confidence"] == 0.1


class TestMnemosyneAPIIntegration:
    """
    Integration tests for Flask routing endpoints.
    """

    def test_get_mnemosyne_cards(self, client):
        response = client.get("/api/mnemosyne/cards")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "cards" in data
        assert data["total_cards"] > 0

        # Check that relation details are populated
        card_procedure = data["cards"]["SOK-PROCEDURE-QUANT-001"]
        assert len(card_procedure["outgoing_links"]) > 0
        assert card_procedure["outgoing_links"][0]["target_id"] == "SOK-MISSION-QUANT-001"

    def test_search_mnemosyne_cards_success(self, client):
        payload = {
            "query": "Hessian trace and Multi-Choice Knapsack budget allocation",
            "top_k": 3
        }
        response = client.post(
            "/api/mnemosyne/search",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert len(data["results"]) > 0
        # The top result should be the Procedure card containing Hessian knapsack details
        assert data["results"][0]["card_id"] == "SOK-PROCEDURE-QUANT-001"
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_search_mnemosyne_cards_missing_param(self, client):
        payload = {
            "top_k": 5
        }
        response = client.post(
            "/api/mnemosyne/search",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_get_cognitive_cycle(self, client):
        """
        Asserts that the GET /api/quantization/cognitive-cycle endpoint returns an
        HTTP 200 status code and the correct JSON schema with fields matching the SOK card families.
        """
        response = client.get("/api/quantization/cognitive-cycle")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "active"
        assert len(data["seven_stages_sequence"]) == 7

        cards = data["sok_card_families"]
        assert cards["SOK-MISSION-QUANT-001"]["family"] == "Mission"
        assert cards["SOK-PROCEDURE-QUANT-001"]["family"] == "Procedure"
        assert cards["SOK-TASK-QUANT-001"]["family"] == "Task"
        assert cards["SOK-EXECUTION-QUANT-001"]["family"] == "Execution"
        assert cards["SOK-REVIEW-QUANT-001"]["family"] == "Review"
        assert cards["SOK-KNOWLEDGE-QUANT-001"]["family"] == "Knowledge"
        assert cards["SOK-IMPROVED-PROCEDURE-QUANT-001"]["family"] == "Improved Procedure"
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_route_mnemosyne_query_high_precision(self, client):
        """
        Asserts that querying with complex, SOK-relevant terms routes the request
        to the High-Precision Target Model.
        """
        payload = {
            "query": "Solve the multi-choice knapsack integer program with average Hessian traces",
            "threshold": 0.40
        }
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        decision = data["routing_decision"]
        assert decision["model_type"] == "high_precision"
        assert "High-Precision" in decision["routed_model"]
        assert decision["precision_allocated"] == "FP16/INT8"
        assert decision["active_ram_footprint_gb"] == 14.0
        assert decision["estimated_latency_ms"] == 55.0
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_route_mnemosyne_query_ultra_light(self, client):
        """
        Asserts that querying with standard, SOK-irrelevant terms routes the request
        to the Ultra-Light Quantized Model, checking size footprint and cost savings.
        """
        payload = {
            "query": "How to make a chocolate chip cookie dessert",
            "threshold": 0.40
        }
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        decision = data["routing_decision"]
        assert decision["model_type"] == "ultra_light"
        assert "Ultra-Light" in decision["routed_model"]
        assert decision["precision_allocated"] == "INT4/Ternary"
        assert decision["active_ram_footprint_gb"] == 0.7
        assert decision["estimated_latency_ms"] == 12.0

        # Check resource impacts
        impact = decision["resource_impact"]
        assert impact["vram_saved_gb"] == 13.3
        assert impact["latency_reduction_percent"] == 78.2
        assert impact["cost_savings_percent"] == 95.0

    def test_route_mnemosyne_query_invalid_params(self, client):
        # Trigger validation failure via missing query parameter
        payload = {"threshold": 0.15}
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

        # Trigger validation failure via non-numeric threshold parameter
        payload = {"query": "test query", "threshold": "invalid_threshold"}
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_feedback_and_self_healing_routing_loop(self, client):
        """
        Verifies the complete reinforcement loop:
        1. Query initially routes to Ultra-Light because similarity is low (< threshold).
        2. SOK card receives 'failure' feedback, driving its confidence score down.
        3. Subsequent Model Router queries dynamically lower the effective threshold,
           forcing self-healing routing of future matches to the High-Precision Target Model.
        """
        card_id = "SOK-MISSION-QUANT-001"
        query_text = "VRAM metrics during high-throughput edge execution"

        # Baseline check: Query gets similarity of ~0.35, routed to ultra-light with threshold 0.45
        payload_route = {
            "query": query_text,
            "threshold": 0.45
        }
        res1 = client.post("/api/mnemosyne/route", data=json.dumps(payload_route), content_type="application/json")
        assert res1.status_code == 200
        assert res1.get_json()["routing_decision"]["model_type"] == "ultra_light"

        # Send failure feedback to drive card confidence down to 0.50 (learning rate 0.50)
        payload_feedback = {
            "card_id": card_id,
            "outcome": "failure",
            "learning_rate": 0.50
        }
        res_feedback = client.post("/api/mnemosyne/feedback", data=json.dumps(payload_feedback), content_type="application/json")
        assert res_feedback.status_code == 200
        assert res_feedback.get_json()["new_card_confidence"] == 0.50

        # Run route query again: effective threshold = 0.45 * 0.50 = 0.225.
        # Max similarity (~0.35) is now >= effective threshold (0.225), forcing high-precision self-healing!
        res2 = client.post("/api/mnemosyne/route", data=json.dumps(payload_route), content_type="application/json")
        assert res2.status_code == 200
        decision = res2.get_json()["routing_decision"]
        assert decision["model_type"] == "high_precision"
        assert decision["best_match_confidence"] == 0.50
        assert decision["effective_threshold"] == 0.225

        # Clean up database confidence state back to 1.0 for subsequent test isolation
        client.post("/api/mnemosyne/feedback", data=json.dumps({"card_id": card_id, "outcome": "success", "learning_rate": 1.0}), content_type="application/json")
