"""
Unit and integration tests for Solomon SOSS Phase 10: Distributed Node Ledger & Phase 11: SOSS Wisdom Layer
"""

import json
import time
import pytest
from app import app, db, distributed_ledger, wisdom_layer
from solomon_distributed_ledger import LedgerBlock


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestDistributedNodeLedger:
    """
    Verifies distributed node state synchronization, SHA-256 sequence block hashes, and SQLite conflict resolution.
    """

    def test_ledger_chain_and_hashing(self):
        ledger = distributed_ledger.__class__(db) # Fresh instance
        assert len(ledger.chain) == 1
        assert ledger.chain[0].previous_hash == "0"

        # Add block
        b1 = ledger.add_block([{"card_id": f"SOK-LEDGER-CARD-{int(time.time())}", "action": "UPSERT", "content": "Ledger state"}])
        assert len(ledger.chain) == 2
        assert b1.previous_hash == ledger.chain[0].hash
        assert ledger.is_chain_valid() is True

    def test_sync_block_to_sqlite_conflict_resolution(self):
        ledger = distributed_ledger.__class__(db)
        uniq_id = f"SOK-SYNCED-CARD-UNIQ-{int(time.time() * 1000) % 1000000}"
        b1 = LedgerBlock(1, ledger.chain[0].hash, [
            {
                "card_id": uniq_id,
                "action": "UPSERT",
                "family": "Knowledge",
                "focus": "Sync test",
                "content": "Sync test content body."
            }
        ])
        success, count, logs = ledger.sync_block_to_sqlite(b1)
        assert success is True
        assert count == 1
        assert uniq_id in logs[0]

        # Verify card exists in central database
        card = db.get_card(uniq_id)
        assert card is not None
        assert card["content"] == "Sync test content body."


class TestSOSS_WisdomLayer:
    """
    Verifies Wisdom Vector limit evaluations, ethical compliance, and human override bypass checks.
    """

    def test_evaluate_wisdom_approved(self):
        approved, msg = wisdom_layer.evaluate_wisdom_vector(
            action_name="Load standard mathematical model",
            confidence=1.2,
            risk_level=2.0
        )
        assert approved is True
        assert "APPROVED" in msg

    def test_evaluate_wisdom_rejected_low_confidence(self):
        approved, msg = wisdom_layer.evaluate_wisdom_vector(
            action_name="Execute highly experimental solver",
            confidence=0.1,
            risk_level=2.0
        )
        assert approved is False
        assert "confidence score" in msg

    def test_evaluate_wisdom_rejected_high_risk(self):
        approved, msg = wisdom_layer.evaluate_wisdom_vector(
            action_name="Force live VM deletion",
            confidence=1.5,
            risk_level=9.5
        )
        assert approved is False
        assert "risk level" in msg

    def test_evaluate_wisdom_rejected_ethics(self):
        approved, msg = wisdom_layer.evaluate_wisdom_vector(
            action_name="evade_detection by casino security",
            confidence=1.8,
            risk_level=1.0
        )
        assert approved is False
        assert "forbidden keyword" in msg

    def test_evaluate_wisdom_human_override_bypass(self):
        approved, msg = wisdom_layer.evaluate_wisdom_vector(
            action_name="Load unverified local library",
            confidence=0.1,
            risk_level=8.5,
            has_human_override=True
        )
        assert approved is True
        assert "HUMAN OVERRIDE" in msg


class TestLedgerAndWisdomAPI:
    """
    Integration tests for Flask API ledger and wisdom validation endpoints.
    """

    def test_api_ledger_sync(self, client):
        uniq_id_api = f"SOK-API-SYNCED-CARD-{int(time.time() * 1000) % 1000000}"
        payload = {
            "index": 1,
            "previous_hash": distributed_ledger.get_latest_block().hash,
            "updates": [
                {
                    "card_id": uniq_id_api,
                    "action": "UPSERT",
                    "content": "API synced content."
                }
            ]
        }
        res = client.post(
            "/api/mnemosyne/ledger/sync",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["synced_count"] == 1
        assert data["ledger_chain_valid"] is True

    def test_api_wisdom_evaluate(self, client):
        payload = {
            "action_name": "Compute local ILP knapsack solutions",
            "confidence": 1.5,
            "risk_level": 1.0,
            "ethics_flagged": False
        }
        res = client.post(
            "/api/mnemosyne/wisdom/evaluate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["approved"] is True
        assert "wisdom_advisory" in data
