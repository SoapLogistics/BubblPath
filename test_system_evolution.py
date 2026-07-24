"""
SOSS Phase 10 & 11: Unit & Integration Test Suite for Evolutionary Features

This suite verifies the complete self-directed curiosity discovery loop and
sandbox scientific experimentation cycle under isolation.
"""

import os
import pytest
import json
from app import app, db
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_prometheus_curiosity import PrometheusCuriosityEngine
from solomon_experiment_engine import ExperimentEngine

# Setup a clean isolated test database path for unit testing
TEST_DB_PATH = "test_evolution.db"

@pytest.fixture
def clean_db():
    # Remove existing test DB if any
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    test_db = SolomonMnemosyneDB(TEST_DB_PATH)
    yield test_db

    # Cleanup after test runs
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Configure Flask app to use clean test database path for endpoint verification
    db.db_path = "test_flask_evolution.db"
    db._init_db()
    with app.test_client() as client:
        yield client
    if os.path.exists("test_flask_evolution.db"):
        os.remove("test_flask_evolution.db")

def test_curiosity_gap_discovery_logic(clean_db):
    """
    Verifies that the Curiosity Engine accurately parses the DB, identifies cards
    with low confidence or sparse relationships as gaps, and ranks them by opportunity weights.
    """
    engine = PrometheusCuriosityEngine(clean_db)

    # Seed one high-confidence, well-linked card
    clean_db.upsert_card("SOK-MISSION-HIGH", "Mission", "High precision target", "Target accuracy is above 99.5 percent.")
    clean_db.update_card_confidence("SOK-MISSION-HIGH", "success", learning_rate=0.5) # confidence climbs above 1.0

    # Seed one low-confidence, isolated card (representing a severe vulnerability gap)
    clean_db.upsert_card("SOK-TASK-LOW", "Task", "Untested edge loading", "Compile outlier bounds dynamically.")
    clean_db.update_card_confidence("SOK-TASK-LOW", "failure", learning_rate=0.5) # confidence drops below 1.0 (to 0.5)

    # Run curiosity discovery
    gaps = engine.discover_gaps()

    assert len(gaps) > 0
    # The low confidence card should be at the top due to higher opportunity weighting
    assert gaps[0]["card_id"] == "SOK-TASK-LOW"
    assert gaps[0]["opportunity_weight"] > 1.5

    # Test curiosity card registration
    curiosity_id = engine.register_curiosity_card(gaps[0])
    assert curiosity_id == "SOK-CURIOSITY-TASK-LOW"

    # Retrieve the new curiosity card and check connections
    cur_card = clean_db.get_card(curiosity_id)
    assert cur_card is not None
    assert "Resolve the cognitive vulnerability identified in SOK-TASK-LOW" in cur_card["content"]
    assert any(link["target_id"] == "SOK-TASK-LOW" for link in cur_card["outgoing_links"])


def test_scientific_experiment_logic_success(clean_db):
    """
    Verifies that when a sandbox experiment succeeds, the Scientific Experiment Engine
    promotes the curiosity card into an APPROVED SOK Procedure card.
    """
    curiosity_id = "SOK-CURIOSITY-TEST-001"
    clean_db.upsert_card(curiosity_id, "Task", "Untested hypothesis", "Analyze GGUF parameters.")

    engine = ExperimentEngine(clean_db)

    code = (
        "def run_trial():\n"
        "    print('SUCCESSFUL_SANDBOX_OUTPUT')\n"
        "    return True\n"
    )
    test_call = "run_trial()"

    report = engine.execute_scientific_experiment(curiosity_id, code, test_call)

    assert report["review_gate_status"] == "APPROVED / ACTIVE"
    assert report["promoted_card_id"] == "SOK-PROMOTED-TEST-001"

    # Verify new card in Mnemosyne
    promoted_card = clean_db.get_card("SOK-PROMOTED-TEST-001")
    assert promoted_card is not None
    assert promoted_card["family"] == "Procedure"
    assert "SUCCESSFUL_SANDBOX_OUTPUT" in promoted_card["content"]


def test_scientific_experiment_logic_failure(clean_db):
    """
    Verifies that when a sandbox experiment fails, the Scientific Experiment Engine
    generates a SOK Failure card and reduces the confidence of the curiosity source card.
    """
    curiosity_id = "SOK-CURIOSITY-FAIL-001"
    clean_db.upsert_card(curiosity_id, "Task", "Vulnerable hypothesis", "Analyze AWQ parameters.")
    original_confidence = clean_db.get_card(curiosity_id)["confidence"]

    engine = ExperimentEngine(clean_db)

    # Code with syntax/runtime error
    code = (
        "def run_broken_trial():\n"
        "    raise ValueError('Simulated Sandbox Exception!')\n"
    )
    test_call = "run_broken_trial()"

    report = engine.execute_scientific_experiment(curiosity_id, code, test_call)

    assert report["review_gate_status"] == "FAILED / REJECTED"
    assert report["promoted_card_id"] == "SOK-PROMOTED-FAIL-001"

    # Verify new Failure card in Mnemosyne
    promoted_card = clean_db.get_card("SOK-PROMOTED-FAIL-001")
    assert promoted_card is not None
    assert promoted_card["family"] == "Failure"
    assert "Simulated Sandbox Exception!" in promoted_card["content"]

    # Verify that confidence score was reduced
    reduced_confidence = clean_db.get_card(curiosity_id)["confidence"]
    assert reduced_confidence < original_confidence


def test_endpoint_curiosity_discover(client):
    """
    Tests the POST /api/mnemosyne/curiosity/discover endpoint.
    """
    # Seed a low confidence card to make sure we discover a gap
    db.upsert_card("SOK-GAP-001", "Mission", "Incomplete", "Lacks coverage.")
    db.update_card_confidence("SOK-GAP-001", "failure", learning_rate=0.8)

    resp = client.post("/api/mnemosyne/curiosity/discover", json={"auto_register": True})
    assert resp.status_code == 200
    data = json.loads(resp.data)

    assert data["status"] == "success"
    assert data["total_gaps_found"] > 0
    assert data["auto_registered_card_id"] is not None
    assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]


def test_endpoint_scientific_experiment(client):
    """
    Tests the POST /api/mnemosyne/experiment/run endpoint with successful and validation failure cases.
    """
    cur_id = "SOK-CURIOSITY-API-001"
    db.upsert_card(cur_id, "Task", "API testing", "Testing endpoint execution.")

    payload = {
        "curiosity_card_id": cur_id,
        "code_under_test": "def solve_me():\n    return 'API_SUCCESS_LOG'\n",
        "test_call": "solve_me()"
    }

    resp = client.post("/api/mnemosyne/experiment/run", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)

    assert data["status"] == "success"
    assert "experiment_report" in data
    assert data["experiment_report"]["review_gate_status"] == "APPROVED / ACTIVE"

    # Verify invalid inputs trigger 400 Bad Request
    resp_invalid = client.post("/api/mnemosyne/experiment/run", json={})
    assert resp_invalid.status_code == 400


# ==========================================
# SOSS PHASE 12: WISDOM LAYER TESTS
# ==========================================
def test_wisdom_layer_unit_logic(clean_db):
    """
    Asserts the unit logic of WisdomLayer under various compliance vector challenges.
    """
    from solomon_wisdom_layer import WisdomLayer
    wl = WisdomLayer(clean_db)

    # Clean, safe operation
    res_ok = wl.evaluate_action("Compile static math formulas inside local context", estimated_ram_mb=120.0)
    assert res_ok["decision"] == "ALLOWED"
    assert res_ok["compliance_score"] >= 0.75
    assert len(res_ok["violations"]) == 0

    # Forbidden malicious payload (Ethics breach)
    res_malicious = wl.evaluate_action("malicious exploit code payload to drop database", estimated_ram_mb=50.0)
    assert res_malicious["decision"] == "BLOCKED"
    assert any("Forbidden" in violation for violation in res_malicious["violations"])

    # Unsafe operation (Safety breach)
    res_unsafe = wl.evaluate_action("Execute script with sudo chmod 777 settings", estimated_ram_mb=50.0)
    assert res_unsafe["decision"] == "BLOCKED"
    assert any("Unsafe OS" in violation for violation in res_unsafe["violations"])

    # Over-resource operation (RAM boundary breach)
    res_oom = wl.evaluate_action("Run highly parallel VM pipeline", estimated_ram_mb=1450.0)
    assert res_oom["decision"] == "BLOCKED"
    assert any("resource footprint" in violation for violation in res_oom["violations"])


def test_endpoint_wisdom_evaluate(client):
    """
    Tests the POST /api/mnemosyne/wisdom/evaluate integration endpoint.
    """
    payload_allow = {
        "query": "Run a standard local cosine similarity scan against knowledge cards",
        "estimated_ram_mb": 50.0
    }
    resp = client.post("/api/mnemosyne/wisdom/evaluate", json=payload_allow)
    assert resp.status_code == 200
    data = json.loads(resp.data)

    assert data["status"] == "success"
    assert data["evaluation"]["decision"] == "ALLOWED"
    assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    payload_block = {
        "query": "rm -rf root configuration files",
        "estimated_ram_mb": 10.0
    }
    resp_block = client.post("/api/mnemosyne/wisdom/evaluate", json=payload_block)
    assert resp_block.status_code == 200
    data_block = json.loads(resp_block.data)
    assert data_block["evaluation"]["decision"] == "BLOCKED"
    assert len(data_block["evaluation"]["violations"]) > 0

    # Test invalid parameter validation
    resp_invalid = client.post("/api/mnemosyne/wisdom/evaluate", json={"query": "test", "estimated_ram_mb": "not-a-float"})
    assert resp_invalid.status_code == 400
