import os
import tempfile
import json
import pytest
from app import app
from solomon_knowledge_cards import MnemosyneRuntime
from solomon_knowledge_cards.schemas import validate_worker_report, validate_review_payload

@pytest.fixture
def temp_db():
    """Fixture that initializes a clean temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def runtime_test(temp_db):
    """Fixture providing a MnemosyneRuntime bound to the temporary database."""
    return MnemosyneRuntime(db_path=temp_db)

@pytest.fixture
def flask_client(temp_db):
    """Fixture providing a Flask test client configured with the temporary database and demo key."""
    os.environ["SOLOMON_DB_PATH"] = temp_db
    os.environ["SOLOMON_ACTIONS_API_KEY"] = "TEST_ACTIONS_API_KEY"

    # Reload runtime in app to use test database & key
    import app as app_module
    app_module.runtime = MnemosyneRuntime(db_path=temp_db)
    app_module.ACTIONS_API_KEY = "TEST_ACTIONS_API_KEY"

    with app_module.app.test_client() as client:
        yield client


# --- 1. Unit Tests for Schema and Security ---

def test_clearance_hierarchy():
    """Verify that hierarchical clearance levels retrieve proper groups."""
    from solomon_knowledge_cards.runtime import get_allowed_clearances

    assert get_allowed_clearances("PUBLIC") == ["PUBLIC"]
    assert get_allowed_clearances("INTERNAL") == ["PUBLIC", "INTERNAL"]
    assert get_allowed_clearances("RESTRICTED") == ["PUBLIC", "INTERNAL", "RESTRICTED"]
    # Default fallback
    assert get_allowed_clearances("UNKNOWN") == ["PUBLIC", "INTERNAL"]


def test_schema_validation_worker_report():
    """Verify worker report dictionary validator enforces strict constraints."""
    valid_report = {
        "report_id": "WR-001",
        "task_id": "TASK-100",
        "outcome": "SUCCESS",
        "worker_id": "openhands-1",
        "worker_type": "OPENHANDS",
        "security_classification": "INTERNAL"
    }
    validated = validate_worker_report(valid_report)
    assert validated["report_id"] == "WR-001"
    assert validated["outcome"] == "SUCCESS"
    assert validated["security_classification"] == "INTERNAL"

    # Missing report_id
    invalid_report = {
        "task_id": "TASK-100",
        "outcome": "SUCCESS"
    }
    with pytest.raises(ValueError, match="missing required key: report_id"):
        validate_worker_report(invalid_report)

    # Invalid outcome
    invalid_outcome = valid_report.copy()
    invalid_outcome["outcome"] = "SUPER_SUCCESS"
    with pytest.raises(ValueError, match="Invalid outcome"):
        validate_worker_report(invalid_outcome)


def test_schema_validation_review():
    """Verify review payload validation rules."""
    valid_review = {
        "card_id": "KC-100",
        "reviewer": "SS3",
        "decision": "APPROVE"
    }
    validated = validate_review_payload(valid_review)
    assert validated["decision"] == "APPROVE"

    # Rejection without reason
    invalid_reject = {
        "card_id": "KC-100",
        "reviewer": "SS3",
        "decision": "REJECT"
    }
    with pytest.raises(ValueError, match="rejection decision requires a reason"):
        validate_review_payload(invalid_reject)


# --- 2. Ingestion & Promotion Lifecycle Tests ---

def test_worker_report_ingestion_and_auto_draft(runtime_test):
    """Verify worker reports are ingested and candidate draft cards are extracted."""
    report = {
        "report_id": "WR-101",
        "task_id": "TASK-101",
        "outcome": "FAILURE",
        "root_cause": "Port collision occurred",
        "repair_action": "Set port environment variable dynamically",
        "security_classification": "INTERNAL",
        "candidate_learning": True
    }

    # Ingest report
    draft_cards = runtime_test.ingest_worker_report(report, source_worker="openhands-1")
    assert len(draft_cards) == 1
    draft_card = draft_cards[0]

    assert draft_card["card_id"] == "KC-DRAFT-WR-101"
    assert draft_card["validation_state"] == "DRAFT"
    assert "Port collision occurred" in draft_card["body"]

    # Test Idempotency / Duplicate protection: Ingesting the same report again returns the same card
    dup_draft_cards = runtime_test.ingest_worker_report(report, source_worker="openhands-1")
    assert len(dup_draft_cards) == 1
    assert dup_draft_cards[0]["card_id"] == "KC-DRAFT-WR-101"


def test_review_lifecycle_transitions(runtime_test):
    """Test entire Review Gate status lifecycle: DRAFT -> REVIEWED -> APPROVED -> ACTIVE."""
    report = {
        "report_id": "WR-202",
        "task_id": "TASK-202",
        "outcome": "SUCCESS",
        "security_classification": "INTERNAL",
        "candidate_learning": True
    }
    drafts = runtime_test.ingest_worker_report(report, source_worker="openhands-1")
    card_id = drafts[0]["card_id"]

    # Transition to REVIEWED
    card = runtime_test.review_card(card_id, "REVIEW", "SS3", notes="Code audit looks clean.")
    assert card["validation_state"] == "REVIEWED"

    # Transition to APPROVED
    card = runtime_test.review_card(card_id, "APPROVE", "SS3")
    assert card["validation_state"] == "APPROVED"

    # Transition to ACTIVE
    card = runtime_test.review_card(card_id, "ACTIVATE", "SS3")
    assert card["validation_state"] == "ACTIVE"

    # Try invalid action (cannot approve an active card)
    with pytest.raises(ValueError):
        runtime_test.review_card(card_id, "APPROVE", "SS3")


def test_card_exclusion_from_retrieval(runtime_test):
    """Verify that only APPROVED or ACTIVE cards are retrieved, and draft/rejected/deprecated are excluded."""
    # 1. Create a draft card via report ingestion
    report = {
        "report_id": "WR-303",
        "task_id": "TASK-303",
        "outcome": "SUCCESS",
        "security_classification": "INTERNAL",
        "candidate_learning": True,
        "attempted": "Running database validation query."
    }
    runtime_test.ingest_worker_report(report, source_worker="openhands-1")
    card_id = "KC-DRAFT-WR-303"

    # Try retrieving context with query matching 'database'
    bundle = runtime_test.retrieve_context(query="database", clearance="INTERNAL")
    # Draft must be excluded
    assert card_id not in bundle["retrieved_card_ids"]

    # Move to APPROVED
    runtime_test.review_card(card_id, "APPROVE", "SS3")
    bundle = runtime_test.retrieve_context(query="database", clearance="INTERNAL")
    # Approved must be included
    assert card_id in bundle["retrieved_card_ids"]

    # Move to DEPRECATED
    runtime_test.review_card(card_id, "DEPRECATE", "SS3")
    bundle = runtime_test.retrieve_context(query="database", clearance="INTERNAL")
    # Deprecated must be excluded
    assert card_id not in bundle["retrieved_card_ids"]


def test_clearance_filtering_and_context_budget(runtime_test):
    """Verify clearance boundaries prevent leaking sensitive cards and enforce budget limits."""
    # Create two approved cards: one PUBLIC, one RESTRICTED
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES
            ('KC-PUB', 'PROCEDURE', 'Public doc', 'Public description', 'Database general tips', 'APPROVED', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-RES', 'REPAIR', 'Restricted secrets', 'Restricted description', 'Database password credentials', 'APPROVED', 'RESTRICTED', '[]', 'now', 'now')
        """)

    # Query with PUBLIC clearance
    public_bundle = runtime_test.retrieve_context(query="Database", clearance="PUBLIC")
    assert "KC-PUB" in public_bundle["retrieved_card_ids"]
    assert "KC-RES" not in public_bundle["retrieved_card_ids"] # prevented leakage!

    # Query with RESTRICTED clearance
    restricted_bundle = runtime_test.retrieve_context(query="Database", clearance="RESTRICTED")
    assert "KC-PUB" in restricted_bundle["retrieved_card_ids"]
    assert "KC-RES" in restricted_bundle["retrieved_card_ids"]


def test_persistence_across_restart(temp_db):
    """Verify cards are persisted to disk and retrieved successfully after runtime process recreation."""
    r1 = MnemosyneRuntime(db_path=temp_db)
    # Manually insert active card
    conn = r1.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES ('KC-PERSIST', 'REPAIR', 'Persist recovery', 'Persist desc', 'Port collison resolved', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now')
        """)
    del r1

    # Simulate restart by instantiating new runtime pointing to same db
    r2 = MnemosyneRuntime(db_path=temp_db)
    bundle = r2.retrieve_context(query="collison", clearance="PUBLIC")
    assert "KC-PERSIST" in bundle["retrieved_card_ids"]


# --- 3. Flask Integration Tests ---

def test_flask_auth_endpoints(flask_client):
    """Verify that protected API endpoints return 401 Unauthorized when token is missing or invalid."""
    # Status endpoint without token
    resp = flask_client.get("/api/command-center/status")
    assert resp.status_code == 401

    # Status endpoint with invalid token
    headers = {"Authorization": "Bearer WRONG_TOKEN"}
    resp = flask_client.get("/api/command-center/status", headers=headers)
    assert resp.status_code == 401

    # Status endpoint with valid token
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}
    resp = flask_client.get("/api/command-center/status", headers=headers)
    assert resp.status_code == 200
    assert resp.json["ok"] is True


def test_flask_full_integration_flow(flask_client):
    """Verify full end-to-end flow: Ingest Worker Report -> Review & Approve -> Retrieve context on Chat."""
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    # 1. Ingest report that generates candidate draft card
    report_payload = {
        "report_id": "WR-FLASK-001",
        "task_id": "TASK-FLASK-001",
        "outcome": "SUCCESS",
        "attempted": "Configure pipeline execution flow",
        "succeeded": "Resolved database memory leak",
        "candidate_learning": True
    }
    ingest_resp = flask_client.post(
        "/api/command-center/worker-report",
        headers=headers,
        json=report_payload
    )
    assert ingest_resp.status_code == 200
    generated_drafts = ingest_resp.json["generated_drafts"]
    assert "KC-DRAFT-WR-FLASK-001" in generated_drafts

    # 2. Transition draft card to APPROVED via SS3 Review route
    review_payload = {
        "card_id": "KC-DRAFT-WR-FLASK-001",
        "reviewer": "SS3",
        "decision": "APPROVE",
        "notes": "End-to-end integration test review"
    }
    review_resp = flask_client.post(
        "/api/command-center/review",
        headers=headers,
        json=review_payload
    )
    assert review_resp.status_code == 200
    assert review_resp.json["validation_state"] == "APPROVED"

    # 3. Request Solomon Chat with matching query terms to trigger context retrieval
    chat_payload = {
        "message": "We need to fix the database memory leak",
        "conversation_id": "CONV-1",
        "request_id": "REQ-1",
        "security_classification": "INTERNAL"
    }
    chat_resp = flask_client.post(
        "/api/command-center/solomon-chat",
        headers=headers,
        json=chat_payload
    )
    assert chat_resp.status_code == 200
    assert chat_resp.json["ok"] is True
    # Confirm that the card was retrieved in chat context telemetry
    retrieved_ids = chat_resp.json["memory"]["retrieved_card_ids"]
    assert "KC-DRAFT-WR-FLASK-001" in retrieved_ids


# --- 4. Autonomous Improvement Loop Tests ---

def test_autonomous_loop_security_scanner(runtime_test):
    """Verify that dangerous patterns fail the static security audit of the AIL daemon."""
    from solomon_knowledge_cards.autonomous_loop import AutonomousImprovementLoop
    loop = AutonomousImprovementLoop(runtime_test)

    # Insecure commands
    bad_code_1 = "import os; os.system('rm -rf /')"
    bad_code_2 = "subprocess.Popen(['ls'], shell=True)"
    bad_code_3 = "eval(input('Enter secret: '))"
    bad_code_4 = "__import__('os').system('chmod 777 file')"

    # Secure commands
    good_code = "def process_data(x):\n    return x * 2\n"

    assert loop.static_security_audit(bad_code_1) is False
    assert loop.static_security_audit(bad_code_2) is False
    assert loop.static_security_audit(bad_code_3) is False
    assert loop.static_security_audit(bad_code_4) is False
    assert loop.static_security_audit(good_code) is True


def test_autonomous_loop_sandbox_and_distill(runtime_test):
    """Verify the discovery and dynamic distillation of safe candidates in the AIL daemon."""
    from solomon_knowledge_cards.autonomous_loop import AutonomousImprovementLoop
    loop = AutonomousImprovementLoop(runtime_test)

    candidate = {
        "name": "Math Doubler Helper",
        "source": "https://github.com/example/math-doubler",
        "code": "def double_value(n):\n    return n * 2\n",
        "description": "Quick mathematical doubling procedure.",
        "type": "MATHEMATICS"
    }

    # Execute cycle
    draft_card = loop.run_discovery_and_absorption(mock_candidate=candidate)

    # Assert successful distillation
    assert draft_card is not None
    assert draft_card["validation_state"] == "DRAFT"
    assert "AIL-DISCOVER-01" in draft_card["title"]
    assert "Math Doubler Helper" in draft_card["body"]

    # Verify candidate is saved in DB but excluded from active retrieval until promoted
    bundle = runtime_test.retrieve_context(query="Doubler", clearance="INTERNAL")
    assert draft_card["card_id"] not in bundle["retrieved_card_ids"]

    # Promote draft card to APPROVED and ACTIVE via Review Gate
    runtime_test.review_card(draft_card["card_id"], "APPROVE", "SS3")
    runtime_test.review_card(draft_card["card_id"], "ACTIVATE", "SS3")

    # Verify now retrieved successfully
    bundle_active = runtime_test.retrieve_context(query="Doubler", clearance="INTERNAL")
    assert draft_card["card_id"] in bundle_active["retrieved_card_ids"]


# --- 5. Relational Linking, Traces, & Resource Monitor Tests ---

def test_card_linking_relations(runtime_test):
    """Verify that card relational links are created, retrieved, and validated."""
    # Insert two active dummy cards
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES
            ('KC-SRC', 'PROCEDURE', 'Source card', 'Desc', 'Procedure details', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-TGT', 'REPAIR', 'Target card', 'Desc', 'Repair details', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now')
        """)

    # Establish a link
    res = runtime_test.add_card_link("KC-SRC", "KC-TGT", "DEPENDS_ON")
    assert res is True

    # Retrieve links
    links = runtime_test.get_card_links("KC-SRC")
    assert len(links) == 1
    assert links[0]["source_id"] == "KC-SRC"
    assert links[0]["target_id"] == "KC-TGT"
    assert links[0]["relationship_type"] == "DEPENDS_ON"


def test_execution_traces_and_visual_path(runtime_test):
    """Verify that step-by-step visual execution traces can be recorded and fetched."""
    runtime_test.add_execution_trace(
        request_id="REQ-TEST-123",
        conversation_id="CONV-TEST-123",
        step_name="Test Step",
        details={"status": "OK", "step": 1}
    )

    conn = runtime_test.db.get_connection()
    try:
        cursor = conn.execute("SELECT * FROM execution_traces WHERE request_id = 'REQ-TEST-123'")
        traces = [dict(r) for r in cursor.fetchall()]
        assert len(traces) == 1
        assert traces[0]["step_name"] == "Test Step"
        assert "status" in json.loads(traces[0]["details"])
    finally:
        conn.close()


def test_resource_monitor_and_capping():
    """Verify that current process memory footprints are retrieved and within caps."""
    from solomon_knowledge_cards import enforce_resource_caps, get_memory_footprint_mb

    mem = get_memory_footprint_mb()
    assert mem > 0.0

    # Under typical test conditions, process is well under 1.5GB (1536MB)
    assert enforce_resource_caps(max_memory_mb=1536.0) is True

    # Test failure case when setting a ridiculously small memory cap
    assert enforce_resource_caps(max_memory_mb=0.01) is False


def test_abort_and_revert_failure_logging(runtime_test):
    """Verify that calling trigger_abort_and_revert registers a FAILURE card in Mnemosyne."""
    from solomon_knowledge_cards.autonomous_loop import AutonomousImprovementLoop
    loop = AutonomousImprovementLoop(runtime_test)

    failure_card_id = loop.trigger_abort_and_revert(
        candidate_name="Crash Candidate",
        error_message="SyntaxError: invalid syntax"
    )

    assert failure_card_id.startswith("KC-DRAFT-WR-FAIL-")

    # Verify the card state is DRAFT and is logged in the database
    conn = runtime_test.db.get_connection()
    try:
        cursor = conn.execute("SELECT * FROM knowledge_cards WHERE card_id = ?", (failure_card_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["card_type"] == "REPAIR"
        assert row["validation_state"] == "DRAFT"
        assert "Crash Candidate" in row["body"]
        assert "SyntaxError: invalid syntax" in row["body"]
    finally:
        conn.close()


def test_flask_bubblepath_endpoints(flask_client):
    """Verify that BubblePath visual synchronization and trace endpoints work via Flask."""
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    # 1. Test Node and Link Graph API
    resp_nodes = flask_client.get("/api/bubblepath/nodes", headers=headers)
    assert resp_nodes.status_code == 200
    assert "nodes" in resp_nodes.json
    assert "edges" in resp_nodes.json

    # 2. Test Execution Path Trace API
    resp_path = flask_client.get("/api/bubblepath/execution-path/REQ-TEST-123", headers=headers)
    assert resp_path.status_code == 200
    assert resp_path.json["request_id"] == "REQ-TEST-123"

    # 3. Test File Sync API (Safe Sandbox Check)
    sync_payload = {
        "filepath": "docs/test_sync.txt",
        "content": "Automated visual node synchronization content."
    }
    resp_sync = flask_client.post("/api/bubblepath/sync-files", headers=headers, json=sync_payload)
    assert resp_sync.status_code == 200
    assert resp_sync.json["filepath"] == "docs/test_sync.txt"

    # Clean up test file
    if os.path.exists("docs/test_sync.txt"):
        os.remove("docs/test_sync.txt")
