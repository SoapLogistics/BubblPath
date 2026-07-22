import os
import tempfile
import json
import pytest
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


def test_flask_legacy_chat_flow(flask_client):
    """Verify legacy /chat route returns backward-compatible format {"reply": "..."}."""
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    # Ingest a card
    report_payload = {
        "report_id": "WR-LEGACY-001",
        "task_id": "TASK-LEGACY-001",
        "outcome": "SUCCESS",
        "attempted": "Legacy configuration",
        "succeeded": "Verify legacy chat route",
        "candidate_learning": True,
        "security_classification": "PUBLIC"
    }
    flask_client.post(
        "/api/command-center/worker-report",
        headers=headers,
        json=report_payload
    )

    # Transition to APPROVED
    review_payload = {
        "card_id": "KC-DRAFT-WR-LEGACY-001",
        "reviewer": "SS3",
        "decision": "APPROVE"
    }
    flask_client.post(
        "/api/command-center/review",
        headers=headers,
        json=review_payload
    )

    # Request legacy chat
    chat_payload = {
        "message": "Verify legacy chat route"
    }
    chat_resp = flask_client.post(
        "/chat",
        json=chat_payload
    )
    assert chat_resp.status_code == 200
    assert "reply" in chat_resp.json
    assert "KC-DRAFT-WR-LEGACY-001" in chat_resp.json["reply"]


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


def test_routing_policy_preferences_and_blocking(flask_client):
    """Verify that operator preferences can be retrieved/updated and enforce blocking policies."""
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    # 1. Test GET preferences endpoint
    resp_get = flask_client.get("/api/command-center/preferences", headers=headers)
    assert resp_get.status_code == 200
    assert resp_get.json["ok"] is True
    prefs = resp_get.json["preferences"]
    assert prefs["execution_mode"] == "solomon_only"
    assert prefs["codex_enabled"] is False
    assert prefs["fallback_to_codex"] is False

    # 2. Test POST to update preferences dynamically
    update_payload = {
        "execution_mode": "custom_mode",
        "codex_enabled": True,
        "fallback_to_codex": True
    }
    resp_post = flask_client.post("/api/command-center/preferences", headers=headers, json=update_payload)
    assert resp_post.status_code == 200
    assert resp_post.json["ok"] is True
    assert resp_post.json["preferences"]["execution_mode"] == "custom_mode"
    assert resp_post.json["preferences"]["codex_enabled"] is True
    assert resp_post.json["preferences"]["fallback_to_codex"] is True

    # Verify update via GET
    resp_get2 = flask_client.get("/api/command-center/preferences", headers=headers)
    assert resp_get2.json["preferences"]["execution_mode"] == "custom_mode"

    # 3. Reset preferences to block Codex execution again
    reset_payload = {
        "execution_mode": "solomon_only",
        "codex_enabled": False,
        "fallback_to_codex": False
    }
    resp_reset = flask_client.post("/api/command-center/preferences", headers=headers, json=reset_payload)
    assert resp_reset.status_code == 200

    # 4. Test programmatic interception & blocking of Codex-targeted tasks
    chat_payload = {
        "message": "Please execute the task immediately using the codex_auto lane",
        "conversation_id": "CONV-TEST-PREFS",
        "request_id": "REQ-TEST-PREFS",
        "security_classification": "INTERNAL"
    }
    resp_chat = flask_client.post("/api/command-center/solomon-chat", headers=headers, json=chat_payload)
    assert resp_chat.status_code == 200
    resp_json = resp_chat.json
    assert resp_json["ok"] is False
    assert resp_json["status"] == "BLOCKED"
    assert resp_json["selected_route"] == "none"
    assert "disabled" in resp_json["error"].lower()


def test_quantization_strategy_and_endpoints(flask_client):
    """Verify that the QuantizationStrategyEngine and its endpoints perform correct dataset compilation and AMPBA simulation."""
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    # 1. Test POST compile calibration dataset endpoint
    resp_compile = flask_client.post("/api/command-center/quantization/compile-calibration", headers=headers)
    assert resp_compile.status_code == 200
    assert resp_compile.json["ok"] is True
    dataset = resp_compile.json["dataset"]
    assert dataset["dataset_name"] == "SOK-Baseline-Calibration" or dataset["dataset_name"] == "SOK-Dynamic-Active-Calibration"
    assert dataset["samples_count"] > 0
    assert len(dataset["calibration_text_blocks"]) > 0

    # 2. Test GET simulate AMPBA bit allocations endpoint
    resp_simulate = flask_client.get(
        "/api/command-center/quantization/simulate-ampba?model=llama3:8b&target_ram_gb=4.5",
        headers=headers
    )
    assert resp_simulate.status_code == 200
    assert resp_simulate.json["ok"] is True
    sim = resp_simulate.json["simulation"]
    assert sim["model_name"] == "llama3:8b"
    assert sim["target_ram_cap_gb"] == 4.5
    assert sim["estimated_quantized_size_gb"] > 0
    assert len(sim["layer_allocations_preview"]) > 0

    # Verify layer-by-layer structure
    layer0 = sim["layer_allocations_preview"][0]
    assert layer0["layer_index"] == 0
    assert "q_proj" in layer0["components"]
    assert "gate_proj" in layer0["components"]
    assert layer0["components"]["q_proj"]["allocated_bits"] in (6, 8)
    assert layer0["components"]["gate_proj"]["allocated_bits"] in (2, 3)


def test_quantization_optimizer_flow(flask_client):
    """Verify that the QuantizationOptimizer class and its compile endpoint function correctly."""
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    # Test GET/POST compile-modelfile endpoint
    resp_modelfile = flask_client.get(
        "/api/command-center/quantization/compile-modelfile?model=llama3:8b&target_ram_gb=4.5",
        headers=headers
    )
    assert resp_modelfile.status_code == 200
    assert resp_modelfile.json["ok"] is True

    # Assert Modelfile contents
    modelfile = resp_modelfile.json["modelfile"]
    assert "FROM llama3:8b" in modelfile
    assert "SYSTEM" in modelfile
    assert "You are Solomon" in modelfile

    # Assert copy-pasteable execution command pipeline
    pipeline = resp_modelfile.json["pipeline"]
    assert "ollama create" in pipeline["ollama_pipeline_command"]
    assert "llama-quantize" in pipeline["llamacpp_pipeline_command"]
    assert pipeline["soss_strategy"] is not None


def test_hybrid_semantic_search_retrieval(runtime_test):
    """Verify hybrid search returns cards via semantic vector matching when literal keywords do not overlap."""
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES
            ('KC-SEM-1', 'REPAIR', 'Docker compose timeout', 'Slow initialization of services', 'Increasing setup startup threshold delays prevents service crashes.', 'APPROVED', 'PUBLIC', '[]', 'now', 'now')
        """)

    # Query using words with partial overlap to trigger the local semantic fallback vectorizer
    # e.g., "compose bootstrap latency"
    # "compose bootstrap latency" has partial overlap with:
    # "Docker compose timeout", "Slow initialization of services", "Increasing setup startup threshold delays prevents service crashes."
    bundle = runtime_test.retrieve_context(query="compose bootstrap latency", clearance="PUBLIC")

    # Assert that the card was retrieved
    assert "KC-SEM-1" in bundle["retrieved_card_ids"]
    assert bundle["retrieval_count"] == 1
    assert "Semantic similarity boost applied" in bundle["memory_context"][0]["reason_selected"]

    # Verify that the embedding was computed and cached back into the database
    cursor = conn.execute("SELECT embedding FROM knowledge_cards WHERE card_id = 'KC-SEM-1'")
    row = cursor.fetchone()
    assert row is not None
    assert row["embedding"] is not None
    emb_data = json.loads(row["embedding"])
    assert len(emb_data) == 128 # deterministic fallback dimension
