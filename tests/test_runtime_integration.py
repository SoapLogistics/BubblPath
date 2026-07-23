import os
import json
import pytest
import datetime
from unittest.mock import patch, MagicMock

# Set test environment
os.environ["OPENAI_API_KEY"] = "mock-key"

from app import app, DB_PATH
from solomon_knowledge_cards.models.card import KnowledgeCard

@pytest.fixture
def client():
    # Configure the Flask app for testing
    app.config["TESTING"] = True

    # We will use an in-memory or temporary test DB for these integration tests
    test_db_path = "solomon_mnemosyne_test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # Patch the global DB references in app
    from solomon_knowledge_cards.storage.db import DatabaseManager
    from solomon_knowledge_cards.api.repository import CardRepository
    from solomon_knowledge_cards.api.review import ReviewGate

    test_db_manager = DatabaseManager(test_db_path)
    test_repo = CardRepository(test_db_manager)
    test_review_gate = ReviewGate(test_db_manager)

    # Temporarily swap app global references
    with patch("app.db_manager", test_db_manager), \
         patch("app.repository", test_repo), \
         patch("app.review_gate", test_review_gate):

        with app.test_client() as client:
            yield client

    # Cleanup test DB
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass

@patch("openai.resources.chat.completions.Completions.create")
def test_chat_retrieval_integration_with_clearance(mock_chat, client):
    # Setup OpenAI mock reply
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Mocked response using memory context."))
    ]
    mock_chat.return_value = mock_response

    # 1. Create a RESTRICTED card and an INTERNAL card
    from app import repository as global_repo
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    restricted_card = KnowledgeCard(
        card_id="RC-RESTRICTED-TEST",
        card_type="REPAIR",
        schema_version="1.0.0",
        title="Top-Secret production workaround",
        summary="Kills process on port 3000",
        body="Secret actions: execute special_remedy.sh",
        status="ACTIVE",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="tester",
        source_type="TEST",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["port", "remedy"],
        security_classification="RESTRICTED",
        evidence="Docker error logs",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future"
    )

    internal_card = KnowledgeCard(
        card_id="RC-INTERNAL-TEST",
        card_type="REPAIR",
        schema_version="1.0.0",
        title="Internal production workaround",
        summary="Standard internal documentation",
        body="Internal actions: standard remediation",
        status="ACTIVE",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="tester",
        source_type="TEST",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["port", "remedy"],
        security_classification="INTERNAL",
        evidence="Docker error logs",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future"
    )

    global_repo.create_card(restricted_card)
    global_repo.create_card(internal_card)

    # 2. Call /chat endpoint with low clearance (PUBLIC)
    response = client.post("/chat", json={
        "message": "I got a port error",
        "security_classification": "PUBLIC"
    })
    assert response.status_code == 200
    res_data = response.get_json()
    assert "RC-RESTRICTED-TEST" not in res_data["retrieved_context"]
    assert "RC-INTERNAL-TEST" not in res_data["retrieved_context"]

    # 3. Call /chat endpoint with standard clearance (INTERNAL)
    response_internal = client.post("/chat", json={
        "message": "I got a port error",
        "security_classification": "INTERNAL"
    })
    assert response_internal.status_code == 200
    res_data_internal = response_internal.get_json()
    assert "RC-RESTRICTED-TEST" not in res_data_internal["retrieved_context"]
    assert "RC-INTERNAL-TEST" in res_data_internal["retrieved_context"]

    # 4. Call /chat endpoint with RESTRICTED clearance
    response_restricted = client.post("/chat", json={
        "message": "I got a port error",
        "security_classification": "RESTRICTED"
    })
    assert response_restricted.status_code == 200
    res_data_restricted = response_restricted.get_json()
    assert "RC-RESTRICTED-TEST" in res_data_restricted["retrieved_context"]
    assert "RC-INTERNAL-TEST" in res_data_restricted["retrieved_context"]

def test_worker_report_extraction_and_review_flow(client):
    # 1. Post a worker failure report
    report_payload = {
        "report": {
            "task_id": "T-INT-101",
            "procedure_id": "PC-SO-01",
            "title": "Compilation task",
            "outcome": "failure",
            "attempted": "Run standard python build.",
            "succeeded": "Parsed dependencies.",
            "failed": "SyntaxError in main.py on line 12.",
            "root_cause": "Missing parenthesis on print statement.",
            "repair_action": "Add parenthesis to line 12 of main.py.",
            "evidence": "SyntaxError: invalid syntax",
            "tags": ["python", "syntax"]
        },
        "review": {
            "is_valid": True,
            "confidence_score": 0.90
        }
    }

    resp = client.post("/worker-report", json=report_payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "Generated 2 candidate cards" in data["message"]

    # Generated cards metadata
    cards = data["cards"]
    assert len(cards) == 2

    fail_card = [c for c in cards if c["card_type"] == "FAILURE"][0]
    repair_card = [c for c in cards if c["card_type"] == "REPAIR"][0]

    assert fail_card["status"] == "DRAFT"
    assert repair_card["status"] == "DRAFT"

    # 2. Verify we can list cards via /cards
    list_resp = client.get("/cards")
    assert list_resp.status_code == 200
    list_data = list_resp.get_json()
    assert list_data["count"] == 2

    # 3. Promote FAILURE card from DRAFT -> REVIEWED via /review
    rev_resp = client.post("/review", json={
        "card_id": fail_card["card_id"],
        "action": "review",
        "notes": "Failure is highly accurate and verified."
    })
    assert rev_resp.status_code == 200
    rev_data = rev_resp.get_json()
    assert rev_data["success"] is True
    assert rev_data["status"] == "REVIEWED"

    # 4. Promote FAILURE card from REVIEWED -> APPROVED
    app_resp = client.post("/review", json={
        "card_id": fail_card["card_id"],
        "action": "approve"
    })
    assert app_resp.status_code == 200
    app_data = app_resp.get_json()
    assert app_data["status"] == "APPROVED"
    assert app_data["validation_state"] == "VALID"

    # 5. Promote FAILURE card from APPROVED -> ACTIVE
    act_resp = client.post("/review", json={
        "card_id": fail_card["card_id"],
        "action": "activate"
    })
    assert act_resp.status_code == 200
    act_data = act_resp.get_json()
    assert act_data["status"] == "ACTIVE"

    # 6. Reject the REPAIR card (DRAFT -> DEPRECATED)
    rej_resp = client.post("/review", json={
        "card_id": repair_card["card_id"],
        "action": "reject",
        "reason": "This is a simple syntax error. No remediation playbook needed."
    })
    assert rej_resp.status_code == 200
    rej_data = rej_resp.get_json()
    assert rej_data["status"] == "DEPRECATED"
    assert rej_data["validation_state"] == "INVALID"
