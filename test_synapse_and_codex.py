"""
Unit and Integration Tests for SOSS Phase 14 and Phase 15 (Synapse blending & Self-Evolving Codex)
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

def test_synapse_mapper_logic():
    mapper = NeuralSynapseMapper(db)
    res = mapper.blend_synapses("DEPENDS_ON")
    assert "synapses" in res
    assert res["synapses_created_count"] >= 0

def test_synapse_endpoint(client):
    resp = client.post("/api/command-center/synapse/blend", json={"relationship_type": "DEPENDS_ON"})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"

def test_codex_compile_logic():
    res = SelfEvolvingCodex.compile_instruction("convert input to uppercase and strip whitespace", "my_strip_fn")
    assert res["status"] == "COMPILED"
    assert "my_strip_fn" in res["source_code"]

def test_codex_compile_endpoint(client):
    payload = {"instruction": "trim whitespace", "function_name": "trim_fn"}
    resp = client.post("/api/command-center/codex/compile", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert data["codex_compilation_result"]["status"] == "COMPILED"
