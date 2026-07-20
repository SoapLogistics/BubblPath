import os
import datetime
import json
import pytest

# Configure a unique test DB path at module level BEFORE importing app
os.environ["SOLOMON_DB_PATH"] = "test_app_only.db"
os.environ["SOLOMON_ACTIONS_API_KEY"] = "secure_test_key"

from app import app, db_manager, repository

@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Clean database before run
    if os.path.exists("test_app_only.db"):
        os.remove("test_app_only.db")
    db_manager._init_db()

    # Explicitly bootstrap legacy checklists for this isolated test DB
    from solomon_knowledge_cards.migrator.importer import DoctrineImporter
    importer = DoctrineImporter(db_manager)
    checklists_dir = "openclaw-workspace/checklists/"
    if os.path.exists(checklists_dir):
        for f in os.listdir(checklists_dir):
            if f.endswith(".md"):
                importer.import_file(os.path.join(checklists_dir, f))

    with app.test_client() as client:
        yield client

    if os.path.exists("test_app_only.db"):
        os.remove("test_app_only.db")

def test_flask_app_endpoints(client):
    # -------------------------------------------------------------
    # 1. Test /api/health Endpoint (Public)
    # -------------------------------------------------------------
    health_response = client.get("/api/health")
    assert health_response.status_code == 200
    health_data = json.loads(health_response.data)
    assert health_data["status"] == "OK"

    # -------------------------------------------------------------
    # 2. Test Authorization Guards (Unauthorized / Forbidden Checks)
    # -------------------------------------------------------------
    # Unauthenticated request should fail
    unauth_response = client.get("/api/command-center/status")
    assert unauth_response.status_code == 401

    # Invalid API key should fail
    forbid_response = client.get("/api/command-center/status", headers={"Authorization": "Bearer bad_key"})
    assert forbid_response.status_code == 403

    # Define headers with valid authorization
    headers = {"Authorization": "Bearer secure_test_key"}

    # -------------------------------------------------------------
    # 3. Test /api/command-center/cards Endpoint
    # -------------------------------------------------------------
    response = client.get("/api/command-center/cards", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "cards" in data
    cards_list = data["cards"]
    assert len(cards_list) > 0
    skill_card = cards_list[0]
    assert skill_card["status"] == "APPROVED"
    assert skill_card["validation_state"] == "VALID"
    assert "legacy" in skill_card["tags"]

    # -------------------------------------------------------------
    # 4. Test /api/command-center/solomon-chat Endpoint
    # -------------------------------------------------------------
    chat_payload = {
        "message": "Verify autonomous loop diagnostics checks and free space.",
        "clearance": "INTERNAL"
    }
    chat_response = client.post("/api/command-center/solomon-chat", json=chat_payload, headers=headers)
    assert chat_response.status_code == 200
    chat_data = json.loads(chat_response.data)
    assert "reply" in chat_data
    assert chat_data["context_injected"] is True

    # -------------------------------------------------------------
    # 5. Test /api/command-center/worker-report Endpoint
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
    report_response = client.post("/api/command-center/worker-report", json=report_payload, headers=headers)
    assert report_response.status_code == 201
    report_data = json.loads(report_response.data)
    assert "draft_cards" in report_data
    drafts = report_data["draft_cards"]
    assert len(drafts) == 2

    fail_card_id = [c["card_id"] for c in drafts if c["card_type"] == "FAILURE"][0]
    repair_card_id = [c["card_id"] for c in drafts if c["card_type"] == "REPAIR"][0]

    # -------------------------------------------------------------
    # 6. Test /api/command-center/review Endpoint
    # -------------------------------------------------------------
    review_payload = {
        "card_id": repair_card_id,
        "target_status": "REVIEWED",
        "updater": "reviewer_john",
        "notes": "Verified timeout solution works."
    }
    review_response = client.post("/api/command-center/review", json=review_payload, headers=headers)
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
    approve_response = client.post("/api/command-center/review", json=approve_payload, headers=headers)
    assert approve_response.status_code == 200
    approve_data = json.loads(approve_response.data)
    assert approve_data["card"]["status"] == "APPROVED"
    assert approve_data["card"]["validation_state"] == "VALID"

    # -------------------------------------------------------------
    # 7. Test Filter /cards with custom keyword query
    # -------------------------------------------------------------
    search_response = client.get("/api/command-center/cards?query=remediation", headers=headers)
    assert search_response.status_code == 200
    search_data = json.loads(search_response.data)
    assert "results" in search_data
