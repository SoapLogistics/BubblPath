"""
Unit and Integration Tests for SOSS Phase 14 (Neural Synapse Mapper) and Phase 15 (Self-Evolving Codex)
"""

import json
import pytest
from app import app, db
from solomon_neural_synapse_mapper import NeuralSynapseMapper
from solomon_self_evolving_codex import SelfEvolvingCodex

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestNeuralSynapseMapper:
    """
    Tests for the Neural Synapse Concept Blender.
    """

    def test_synapse_blending_persistence(self):
        mapper = NeuralSynapseMapper(db)

        # Blend standard SOK cards
        res = mapper.blend_knowledge_cards("SOK-MISSION-QUANT-001", "SOK-TASK-QUANT-001")
        assert res["status"] == "success"
        blended_id = res["blended_concept_id"]
        assert "BLENDED" in blended_id
        assert res["db_persisted"] is True

        # Retrieve card to verify contents
        card = db.get_card(blended_id)
        assert card["status"] == "ACTIVE"
        assert "Unified Concept:" in card["focus"]


class TestSelfEvolvingCodex:
    """
    Tests for Natural Language Compiler.
    """

    def test_codex_compilation_success(self):
        codex = SelfEvolvingCodex(db)

        # Complies and sandbox-tests Fahrenheit converter
        res = codex.compile_natural_language_intent(
            tool_name="temp-converter",
            natural_language_intent="convert fahrenheit to celsius",
            expected_output_assertion="assert abs(fahr_to_cels(32.0) - 0.0) < 1e-5"
        )
        assert res["status"] == "success"
        assert res["db_registered"] is True
        assert res["card_id"] == "SOK-CODEX-TEMP_CONVERTER"


class TestSynapseCodexAPIIntegration:
    """
    Verifies REST routes for Synapse blending and Codex compilations.
    """

    def test_post_synapse_blend_endpoint(self, client):
        payload = {
            "card_id_1": "SOK-PROCEDURE-QUANT-001",
            "card_id_2": "SOK-TASK-QUANT-001"
        }
        response = client.post("/api/command-center/synapse/blend", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "blended_concept_id" in data
        assert data["db_persisted"] is True

    def test_post_codex_compile_endpoint(self, client):
        payload = {
            "tool_name": "list-counter",
            "natural_language_intent": "get list element count",
            "expected_output_assertion": "assert get_element_count([1, 2, 3, 4]) == 4"
        }
        response = client.post("/api/command-center/codex/compile", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["db_registered"] is True
        assert data["card_id"] == "SOK-CODEX-LIST_COUNTER"
