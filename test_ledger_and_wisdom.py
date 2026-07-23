"""
Unit and Integration Tests for SOSS Phase 10 (Distributed Ledger) and Phase 11 (Wisdom Layer)
"""

import json
import pytest
from app import app, db
from solomon_distributed_ledger import DistributedNodeLedger
from solomon_wisdom_layer import SOSS_WisdomLayer

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestDistributedLedger:
    """
    Tests for the cryptographic Distributed Node Ledger.
    """

    def test_ledger_sync_integrity(self):
        ledger = DistributedNodeLedger("solomon_mnemosyne_demo.db")

        # Ingest first block
        res1 = ledger.sync_node_event(
            node_id="ubuntu_node_01",
            node_type="ubuntu_server",
            event_type="REPAIR_EXECUTED",
            payload={"action": "reindexed_database_indices"}
        )
        assert res1["status"] == "success"
        hash1 = res1["ledger_block_hash"]

        # Ingest second block (verifies previous_hash tracking)
        res2 = ledger.sync_node_event(
            node_id="ubuntu_node_01",
            node_type="ubuntu_server",
            event_type="REPAIR_EXECUTED",
            payload={"action": "garbage_collection_ran"}
        )
        assert res2["status"] == "success"
        hash2 = res2["ledger_block_hash"]
        assert hash1 != hash2


class TestWisdomLayer:
    """
    Tests for the SOSS Phase 11 Wisdom Gate safety constraints.
    """

    def test_wisdom_scoring_thresholds(self):
        gate = SOSS_WisdomLayer()

        # Case 1: High Confidence, Low Risk, Perfect Ethics -> APPROVED
        res_ok = gate.evaluate_wisdom_vector(
            skill_name="jules_addition_tool",
            confidence=1.8,
            risks=0.1,
            ethics_limits=0.0
        )
        assert res_ok["status"] == "APPROVED"
        assert res_ok["blocked"] is False
        assert res_ok["resolved_wisdom_score"] == 0.870 # 0.5*1.8 - 0.3*0.1 - 0 = 0.90 - 0.03 = 0.87

        # Case 2: High Risk, Low Confidence -> BLOCKED_RISK_BREACH
        res_risky = gate.evaluate_wisdom_vector(
            skill_name="raw_eval_execution",
            confidence=0.4,
            risks=0.9,
            ethics_limits=0.1
        )
        assert res_risky["status"] == "BLOCKED_RISK_BREACH"
        assert res_risky["blocked"] is True

        # Case 3: Ethics Violations -> BLOCKED_ETHICS_VIOLATION
        res_ethical = gate.evaluate_wisdom_vector(
            skill_name="malicious_credential_harvester",
            confidence=1.8,
            risks=0.1,
            ethics_limits=0.75
        )
        assert res_ethical["status"] == "BLOCKED_ETHICS_VIOLATION"
        assert res_ethical["blocked"] is True


class TestLedgerWisdomAPIIntegration:
    """
    Verifies REST routes for Distributed Ledger Sync and Wisdom evaluations.
    """

    def test_post_distributed_ledger_sync_endpoint(self, client):
        payload = {
            "node_id": "macOS_client_99",
            "node_type": "macOS_client",
            "event_type": "KNOWLEDGE_ACQUIRED",
            "payload": {
                "card_id": "SOK-DIST-SYNC-099",
                "family": "Knowledge",
                "focus": "Dynamic caching rule verified on macOS",
                "content": "Flushing intermediate model layouts reduces memory leakage on M2 chips."
            }
        }
        response = client.post("/api/command-center/ledger/sync", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["node_id"] == "macOS_client_99"
        assert "ledger_block_hash" in data

        # Check propagation to primary database
        card = db.get_card("SOK-DIST-SYNC-099")
        assert card["status"] == "ACTIVE"
        assert "Flushing intermediate model layouts" in card["content"]

    def test_post_wisdom_evaluate_endpoint_blocked(self, client):
        payload = {
            "skill_name": "malicious_exploit_module",
            "confidence": 1.5,
            "risks": 0.4,
            "ethics_limits": 0.80
        }
        response = client.post("/api/command-center/wisdom/evaluate", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "BLOCKED_ETHICS_VIOLATION"
        assert data["blocked"] is True
        assert "violates Solomon ethical guidelines" in data["message"]
