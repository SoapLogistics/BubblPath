import os
import json
import pytest
from app import app, db_manager

@pytest.fixture
def client():
    # Use testing mode
    app.config["TESTING"] = True
    # Explicitly configure a separate test DB path for app integration testing
    test_db = "test_app_integration.db"
    os.environ["SOLOMON_DB_PATH"] = test_db

    with app.test_client() as client:
        yield client

    # Clean up test DB file
    if os.path.exists(test_db):
        os.remove(test_db)

def test_flask_app_endpoints(client):
    # -------------------------------------------------------------
    # 1. Test /cards Endpoint (listing pre-bootstrapped legacy checklists)
    # -------------------------------------------------------------
    response = client.get("/cards")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "cards" in data
    # Some cards from checklists should have been bootstrapped on boot
    cards_list = data["cards"]
    assert len(cards_list) > 0
    # Locate one card and verify its properties
    skill_card = cards_list[0]
    assert skill_card["status"] == "APPROVED"
    assert skill_card["validation_state"] == "VALID"
    assert "legacy" in skill_card["tags"]

    # -------------------------------------------------------------
    # 2. Test /chat Endpoint with context injection
    # -------------------------------------------------------------
    # Search for something related to autonomous cycle
    chat_payload = {
        "message": "Verify autonomous loop diagnostics checks and free space.",
        "clearance": "INTERNAL"
    }
    chat_response = client.post("/chat", json=chat_payload)
    assert chat_response.status_code == 200
    chat_data = json.loads(chat_response.data)
    assert "reply" in chat_data
    # Should have retrieved the bootstrapped Master Procedure Card for Autonomous Cycle!
    assert chat_data["context_injected"] is True

    # -------------------------------------------------------------
    # 3. Test /worker-report Endpoint (Extraction Ingestion)
    # -------------------------------------------------------------
    report_payload = {
        "report": {
            "task_id": "T-FLASK-TEST",
            "procedure_id": "PC-SO-01",
            "title": "Local pip install run",
            "outcome": "failure",
            "attempted": "Pip install requirement libraries.",
            "succeeded": "Parsed environment.yaml",
            "failed": "Connection timeout fetching wheels on pip network",
            "root_cause": "Remote mirror rate-limited",
            "repair_action": "Set PIP_DEFAULT_TIMEOUT=120 and try again.",
            "evidence": "socket.timeout on pypi.org connection",
            "tags": ["flask-pip", "timeout"]
        }
    }
    report_response = client.post("/worker-report", json=report_payload)
    assert report_response.status_code == 201
    report_data = json.loads(report_response.data)
    assert "draft_cards" in report_data
    # Should extract a FAILURE card and a REPAIR card
    drafts = report_data["draft_cards"]
    assert len(drafts) == 2

    fail_card_id = [c["card_id"] for c in drafts if c["card_type"] == "FAILURE"][0]
    repair_card_id = [c["card_id"] for c in drafts if c["card_type"] == "REPAIR"][0]

    # -------------------------------------------------------------
    # 4. Test /review Endpoint (Promotion Status Gates)
    # -------------------------------------------------------------
    # Try promoting the extracted repair card from DRAFT to REVIEWED
    review_payload = {
        "card_id": repair_card_id,
        "target_status": "REVIEWED",
        "updater": "reviewer_john",
        "notes": "Verified timeout solution works."
    }
    review_response = client.post("/review", json=review_payload)
    assert review_response.status_code == 200
    review_data = json.loads(review_response.data)
    assert review_data["card"]["status"] == "REVIEWED"
    assert review_data["card"]["extra_metadata"]["review_notes"] == "Verified timeout solution works."

    # Try promoting from REVIEWED to APPROVED
    approve_payload = {
        "card_id": repair_card_id,
        "target_status": "APPROVED",
        "updater": "approver_alice"
    }
    approve_response = client.post("/review", json=approve_payload)
    assert approve_response.status_code == 200
    approve_data = json.loads(approve_response.data)
    assert approve_data["card"]["status"] == "APPROVED"
    assert approve_data["card"]["validation_state"] == "VALID"

    # -------------------------------------------------------------
    # 5. Test Filter /cards with custom keyword query
    # -------------------------------------------------------------
    search_response = client.get("/cards?query=remediation")
    assert search_response.status_code == 200
    search_data = json.loads(search_response.data)
    assert "results" in search_data
