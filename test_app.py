import json
import os
import pytest
from unittest.mock import MagicMock, patch
from app import app, client, routing_preferences, worker_modes, SOK_CARDS_FILE, SOK_LINKS_FILE, TELEMETRY_LOG_FILE, TargetSynthesizedClass, sql_query_latency_speeds

@pytest.fixture
def flask_client():
    app.config["TESTING"] = True
    # Clean up card database and links before test runs
    for f in [SOK_CARDS_FILE, SOK_LINKS_FILE, TELEMETRY_LOG_FILE]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

    # Reset latency metrics
    sql_query_latency_speeds.clear()

    with app.test_client() as client:
        yield client

    # Clean up after test runs
    for f in [SOK_CARDS_FILE, SOK_LINKS_FILE, TELEMETRY_LOG_FILE]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

def test_health_endpoint(flask_client):
    """Verifies that the telemetry health probe works as expected."""
    response = flask_client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "memory_rss_bytes" in data
    assert "memory_rss_formatted" in data

def test_metrics_endpoint(flask_client):
    """Verifies that the telemetry metrics works."""
    response = flask_client.get("/metrics")
    assert response.status_code == 200
    data = response.get_json()
    assert "sql_query_latency_speeds" in data
    assert "ast_fusion_stats" in data

def test_preferences_endpoint(flask_client):
    """Verifies retrieval and update of preferences."""
    # GET preferences
    response = flask_client.get("/api/command-center/preferences")
    assert response.status_code == 200
    data = response.get_json()
    assert "execution_mode" in data

    # POST preferences
    update_payload = {
        "execution_mode": "solomon_only",
        "codex_enabled": False,
        "fallback_to_codex": False
    }
    response2 = flask_client.post(
        "/api/command-center/preferences",
        data=json.dumps(update_payload),
        content_type="application/json"
    )
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert data2["status"] == "updated"
    assert data2["preferences"]["execution_mode"] == "solomon_only"
    assert data2["preferences"]["codex_enabled"] is False

    # Restore preferences
    flask_client.post(
        "/api/command-center/preferences",
        data=json.dumps({"execution_mode": "hybrid", "codex_enabled": True, "fallback_to_codex": True}),
        content_type="application/json"
    )

def test_worker_modes_endpoint(flask_client):
    """Verifies retrieval and updates of worker execution modes."""
    # GET worker modes
    response = flask_client.get("/api/command-center/worker-modes")
    assert response.status_code == 200
    data = response.get_json()
    assert data["Gabriel"] == "READ_ONLY"

    # POST worker modes
    response2 = flask_client.post(
        "/api/command-center/worker-modes",
        data=json.dumps({"Gabriel": "LIVE", "Loki": "LIVE"}),
        content_type="application/json"
    )
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert data2["worker_modes"]["Gabriel"] == "LIVE"
    assert data2["worker_modes"]["Loki"] == "LIVE"

    # Restore worker modes
    flask_client.post(
        "/api/command-center/worker-modes",
        data=json.dumps({"Gabriel": "READ_ONLY", "Loki": "RESEARCH_ONLY"}),
        content_type="application/json"
    )

def test_quantization_blueprint_endpoint(flask_client):
    """Verifies feasibility blueprints are retrieved."""
    response = flask_client.get("/api/quantization/blueprint")
    assert response.status_code == 200
    data = response.get_json()
    assert data["feasibility_status"] == "HIGHLY_FEASIBLE"
    assert len(data["layers"]) == 4

def test_quantization_simulate_endpoint(flask_client):
    """Verifies AMPBA simulations."""
    response = flask_client.post(
        "/api/quantization/simulate",
        data=json.dumps({"ram_ceiling_gb": 8.0}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert data["target_ram_ceiling_gb"] == 8.0
    assert "average_allocated_bitwidth" in data

def test_cognitive_cycle_endpoint(flask_client):
    """Verifies SOK sequence steps retrieval."""
    response = flask_client.get("/api/quantization/cognitive-cycle")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["cycle_stages"]) == 7

def test_mnemosyne_cards_endpoint(flask_client):
    """Verifies Mnemosyne card retrieval and persistent insert capabilities."""
    # GET active cards
    response = flask_client.get("/api/mnemosyne/cards?status=ACTIVE")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # POST insert a new SOK memory card
    payload = {
        "title": "Local GGUF Calibration Profiles",
        "category": "Quantization",
        "status": "ACTIVE",
        "content": "Calibrated offsets for Llama-3-8B model layers running local offloading.",
        "confidence": 1.9
    }
    response_post = flask_client.post(
        "/api/mnemosyne/cards",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response_post.status_code == 201
    post_data = response_post.get_json()
    assert post_data["status"] == "success"
    assert post_data["card"]["title"] == "Local GGUF Calibration Profiles"

    # Assert persistence by reloading database
    response_check = flask_client.get("/api/mnemosyne/cards?status=ACTIVE")
    data_check = response_check.get_json()
    titles = [c["title"] for c in data_check]
    assert "Local GGUF Calibration Profiles" in titles

def test_mnemosyne_search_endpoint(flask_client):
    """Verifies mock semantic search rankings and cosine boundaries."""
    response = flask_client.post(
        "/api/mnemosyne/search",
        data=json.dumps({"query": "Ternary SpinQuant optimization"}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert len(data["results"]) >= 1
    # Check that cosine boundaries division-by-zero protection holds
    for item in data["results"]:
        assert -1.0 <= item["similarity_score"] <= 1.0

def test_mnemosyne_route_endpoint(flask_client):
    """Verifies dynamic model router hot-swapping based on SOK card confidence."""
    # Match high confidence card (BitNet b1.58 confidence is 2.0 >= 1.5) -> INT4
    response1 = flask_client.post(
        "/api/mnemosyne/route",
        data=json.dumps({"query": "Explain BitNet b1.58 ternary weights"}),
        content_type="application/json"
    )
    assert response1.status_code == 200
    data1 = response1.get_json()
    assert data1["routed_model"] == "Ultra-Light INT4 Quantized Model"
    assert data1["confidence"] == 2.0

    # Match low confidence or no matched cards -> FP16
    response2 = flask_client.post(
        "/api/mnemosyne/route",
        data=json.dumps({"query": "Completely unknown query subject"}),
        content_type="application/json"
    )
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert data2["routed_model"] == "High-Precision FP16 Model"

def test_mnemosyne_feedback_endpoint(flask_client):
    """Verifies feedback scaling with clipping bounds [0.1, 2.0]."""
    response = flask_client.post(
        "/api/mnemosyne/feedback",
        data=json.dumps({"card_id": 1, "rating": 1}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["card"]["confidence"] <= 2.0

    # Test error fallback
    response_err = flask_client.post(
        "/api/mnemosyne/feedback",
        data=json.dumps({"card_id": 999, "rating": 1}),
        content_type="application/json"
    )
    assert response_err.status_code == 404

def test_crucible_dynamic_adaptation(flask_client):
    """Verifies that the performance crucible dynamically selects AST pruning modes when latency increases."""
    # Scenario A: Normal database search latency
    response_norm = flask_client.post(
        "/api/mnemosyne/crucible",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response_norm.status_code == 200
    data_norm = response_norm.get_json()
    assert data_norm["crucible_mode"] == "AST-FUSION"

    # Seed heavy query latency speeds
    sql_query_latency_speeds.extend([12.5, 15.0, 11.2, 9.8, 14.5, 16.2])

    # Scenario B: Delayed search latency triggers active AST-PRUNE to release bottleneck
    response_delay = flask_client.post(
        "/api/mnemosyne/crucible",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response_delay.status_code == 200
    data_delay = response_delay.get_json()
    assert data_delay["crucible_mode"] == "AST-PRUNE"
    assert "dead-path" in data_delay["optimization_delta"]

def test_ast_inject_endpoint(flask_client):
    """Verifies AST compiling and live class-method injection at runtime."""
    # Failure case: missing key
    response1 = flask_client.post(
        "/api/mnemosyne/ast-inject",
        data=json.dumps({"class_name": "TargetSynthesizedClass"}),
        content_type="application/json"
    )
    assert response1.status_code == 400

    # Failure case: bad code compilation error
    response_bad = flask_client.post(
        "/api/mnemosyne/ast-inject",
        data=json.dumps({
            "class_name": "TargetSynthesizedClass",
            "method_name": "broken_syntax",
            "method_code": "def broken_syntax(self):\n   return (123\n" # Missing closing paren
        }),
        content_type="application/json"
    )
    assert response_bad.status_code == 500
    assert "AST Compilation Exception" in response_bad.get_json()["error"]

    # Success case: live compilation and attr binding
    success_code = (
        "def dynamic_add(self, a, b):\n"
        "    return a + b\n"
    )
    response2 = flask_client.post(
        "/api/mnemosyne/ast-inject",
        data=json.dumps({
            "class_name": "TargetSynthesizedClass",
            "method_name": "dynamic_add",
            "method_code": success_code
        }),
        content_type="application/json"
    )
    assert response2.status_code == 200
    data = response2.get_json()
    assert data["status"] == "SUCCESS"
    assert data["injected_method"] == "dynamic_add"
    assert data["hot_reload_complete"] is True

    # Real target evaluation: instantiate the class and call our dynamically compiled method!
    obj = TargetSynthesizedClass()
    assert hasattr(obj, "dynamic_add")
    res_val = obj.dynamic_add(15, 25) # 15 + 25 = 40
    assert res_val == 40

def test_observe_endpoint(flask_client):
    """Verifies blackbox profiling synthesis."""
    response = flask_client.post(
        "/api/mnemosyne/observe",
        data=json.dumps({"binary_name": "kubernetes-cli", "command": "kubectl get pods"}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["binary_profiled"] == "kubernetes-cli"
    assert "synthesized_clean_room_python" in data

def test_skills_endpoint_and_sandbox_run(flask_client):
    """Verifies active capability graph and isolated sandbox execute lanes (live & mock)."""
    # GET skills
    response1 = flask_client.get("/api/mnemosyne/skills")
    assert response1.status_code == 200
    data1 = response1.get_json()
    assert len(data1["skills"]) == 4

    # POST execute skill failure
    response2 = flask_client.post(
        "/api/mnemosyne/skills/execute",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response2.status_code == 400

    # POST execute skill success mock
    response3 = flask_client.post(
        "/api/mnemosyne/skills/execute",
        data=json.dumps({"skill_id": "codex_mcp_bridge"}),
        content_type="application/json"
    )
    assert response3.status_code == 200
    data3 = response3.get_json()
    assert data3["execution_status"] == "SUCCESS"

    # POST execute skill with live python script inside subprocess sandbox
    real_python_code = (
        "import sys\n"
        "sys.stdout.write('Solomon sandbox run was successful')\n"
        "sys.exit(0)\n"
    )
    response4 = flask_client.post(
        "/api/mnemosyne/skills/execute",
        data=json.dumps({"skill_id": "jules_test_runner_loop", "code": real_python_code}),
        content_type="application/json"
    )
    assert response4.status_code == 200
    data4 = response4.get_json()
    assert data4["execution_status"] == "SUCCESS"
    assert data4["exit_code"] == 0
    assert "sandbox run" in data4["stdout"]

    # POST execute skill with failing script inside sandbox to test error reporting
    failing_python_code = (
        "raise ValueError('Simulated compilation error')\n"
    )
    response5 = flask_client.post(
        "/api/mnemosyne/skills/execute",
        data=json.dumps({"skill_id": "jules_test_runner_loop", "code": failing_python_code}),
        content_type="application/json"
    )
    assert response5.status_code == 200
    data5 = response5.get_json()
    assert data5["execution_status"] == "FAILED"
    assert data5["exit_code"] != 0
    assert "Simulated compilation error" in data5["stderr"]

def test_topological_skill_graph_execution(flask_client):
    """Verifies sequential sandboxed execution in exact topologically sorted chronological order."""
    # Build execution codes where dependency runs first, followed by dependent
    dependency_code = "import sys; sys.stdout.write('Ran Jules Test Loop \\n')"
    dependent_code = "import sys; sys.stdout.write('Ran Parallel Worktree')"

    payload = {
        "skill_id": "codex_parallel_worktrees",
        "codes": {
            "jules_test_runner_loop": dependency_code,
            "codex_parallel_worktrees": dependent_code
        }
    }

    response = flask_client.post(
        "/api/mnemosyne/skills/execute-graph",
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["graph_execution_status"] == "SUCCESS"
    assert data["target_skill_id"] == "codex_parallel_worktrees"

    # Assert sequence order of results: dependency 'jules_test_runner_loop' must execute BEFORE 'codex_parallel_worktrees'
    history = data["execution_history"]
    assert len(history) == 2
    assert history[0]["skill_id"] == "jules_test_runner_loop"
    assert history[1]["skill_id"] == "codex_parallel_worktrees"
    assert "Ran Jules Test Loop" in history[0]["stdout"]
    assert "Ran Parallel Worktree" in history[1]["stdout"]

def test_self_heal_endpoint(flask_client):
    """Verifies that the AST Self-Correction and Capability Promotion GCPP works."""
    # 1. Validation checks
    response_val = flask_client.post(
        "/api/mnemosyne/skills/self-heal",
        data=json.dumps({"skill_id": "jules_dynamic_autonomer"}),
        content_type="application/json"
    )
    assert response_val.status_code == 400

    # 2. Live execution of a code with errors (triggers correction and promotion!)
    err_code = "raise ValueError('Simulated compilation error')\n"
    response_run = flask_client.post(
        "/api/mnemosyne/skills/self-heal",
        data=json.dumps({"skill_id": "jules_dynamic_autonomer", "code": err_code}),
        content_type="application/json"
    )
    assert response_run.status_code == 200
    data_run = response_run.get_json()
    assert data_run["self_healing_status"] == "SUCCESSFUL"
    assert data_run["total_attempts"] == 2
    assert "self-healed after compile error" in data_run["stdout"]
    assert data_run["promoted_to_active"] is True

    # 3. Assert card was promoted to ACTIVE in Mnemosyne
    response_check = flask_client.get("/api/mnemosyne/cards?status=ACTIVE")
    cards = response_check.get_json()
    promoted_card = [c for c in cards if "jules_dynamic_autonomer" in c["title"]]
    assert len(promoted_card) == 1
    assert promoted_card[0]["status"] == "ACTIVE"

    # 4. Assert skill registry added the capability
    response_skills = flask_client.get("/api/mnemosyne/skills")
    skills = response_skills.get_json()["skills"]
    registered_ids = [s["id"] for s in skills]
    assert "jules_dynamic_autonomer" in registered_ids

def test_semantic_graph_links_endpoints(flask_client):
    """Verifies directed link creation, deduplication, and topological graph traversal."""
    # 1. Post dynamic directed card link relation
    response_link = flask_client.post(
        "/api/mnemosyne/cards/links",
        data=json.dumps({"source_id": 1, "target_id": 2, "relationship_type": "PREVENTS"}),
        content_type="application/json"
    )
    assert response_link.status_code == 201
    data_link = response_link.get_json()
    assert data_link["status"] == "success"
    assert data_link["link"]["relationship_type"] == "PREVENTS"

    # 1b. Duplicate check
    response_dup = flask_client.post(
        "/api/mnemosyne/cards/links",
        data=json.dumps({"source_id": 1, "target_id": 2, "relationship_type": "PREVENTS"}),
        content_type="application/json"
    )
    assert response_dup.status_code == 200
    assert response_dup.get_json()["status"] == "duplicate_ignored"

    # 2. Get and traverse the topological card graph
    response_graph = flask_client.get("/api/mnemosyne/cards/graph")
    assert response_graph.status_code == 200
    data_graph = response_graph.get_json()
    assert len(data_graph["nodes"]) >= 3
    assert len(data_graph["edges"]) >= 3
    assert data_graph["cycle_detected_in_linkage_graph"] is False
    assert data_graph["is_safe_for_topological_execution"] is True

    # 3. Insert a cyclic loop relationship to assert cycle detection
    flask_client.post(
        "/api/mnemosyne/cards/links",
        data=json.dumps({"source_id": 2, "target_id": 1, "relationship_type": "DEPENDS_ON"}),
        content_type="application/json"
    )
    response_cycle = flask_client.get("/api/mnemosyne/cards/graph")
    assert response_cycle.status_code == 200
    data_cycle = response_cycle.get_json()
    assert data_cycle["cycle_detected_in_linkage_graph"] is True
    assert data_cycle["is_safe_for_topological_execution"] is False

def test_resource_guardrails_compaction(flask_client):
    """Verifies telemetry RSS tracking and automatic memory compaction triggers."""
    # Seed a DRAFT card with low confidence
    flask_client.post(
        "/api/mnemosyne/cards",
        data=json.dumps({"title": "Temporary Draft Leak", "status": "DRAFT", "confidence": 0.5}),
        content_type="application/json"
    )

    # Verify the card is added
    response_get = flask_client.get("/api/mnemosyne/cards?status=DRAFT")
    assert len(response_get.get_json()) == 1

    # Programmatically trigger safe/normal resource guardrails check (no compaction)
    response_safe = flask_client.post(
        "/api/command-center/guardrails",
        data=json.dumps({"forced_rss_bytes": 500 * 1024 * 1024}), # 500MB
        content_type="application/json"
    )
    assert response_safe.status_code == 200
    assert response_safe.get_json()["compaction_triggered"] is False

    # Programmatically trigger resource limit violations (>1.5GB) to initiate active compaction
    response_violate = flask_client.post(
        "/api/command-center/guardrails",
        data=json.dumps({"forced_rss_bytes": 2 * 1024 * 1024 * 1024}), # 2GB
        content_type="application/json"
    )
    assert response_violate.status_code == 200
    data_violate = response_violate.get_json()
    assert data_violate["compaction_triggered"] is True
    assert data_violate["purged_cards_count"] >= 1

    # Assert that the DRAFT card was purged successfully
    response_check = flask_client.get("/api/mnemosyne/cards?status=DRAFT")
    assert len(response_check.get_json()) == 0

    # Verify plain-text telemetry log exists and has content
    assert os.path.exists(TELEMETRY_LOG_FILE)
    with open(TELEMETRY_LOG_FILE, "r", encoding="utf-8") as f:
        log_text = f.read()
        assert "Compaction_Triggered: True" in log_text

def test_ail_daemon_security_audits(flask_client):
    """Verifies static security audits, blocked loops, evaluation escapes, and rollbacks inside AIL."""
    # Loop Block
    response_loop = flask_client.post(
        "/api/mnemosyne/ail/daemon",
        data=json.dumps({"code": "while True: pass"}),
        content_type="application/json"
    )
    assert response_loop.status_code == 400
    data_loop = response_loop.get_json()
    assert data_loop["status"] == "REJECTED"
    assert data_loop["git_revert_complete"] is True

    # Eval Escape Block
    response_eval = flask_client.post(
        "/api/mnemosyne/ail/daemon",
        data=json.dumps({"code": "eval('2+2')"}),
        content_type="application/json"
    )
    assert response_eval.status_code == 400
    assert response_eval.get_json()["rollback_triggered"] is True

    # Safe Exec Approval
    response_safe = flask_client.post(
        "/api/mnemosyne/ail/daemon",
        data=json.dumps({"code": "import sys; sys.stdout.write('Clean loop approved')"}),
        content_type="application/json"
    )
    assert response_safe.status_code == 200
    data_safe = response_safe.get_json()
    assert data_safe["status"] == "APPROVED"
    assert data_safe["rollback_triggered"] is False
    assert "Clean loop approved" in data_safe["stdout"]

    # Sandbox Crash Rollback Trigger
    response_crash = flask_client.post(
        "/api/mnemosyne/ail/daemon",
        data=json.dumps({"code": "raise KeyError('Simulate runtime error')"}),
        content_type="application/json"
    )
    assert response_crash.status_code == 200
    data_crash = response_crash.get_json()
    assert data_crash["status"] == "ROLLBACK_TRIGGERED"
    assert data_crash["rollback_triggered"] is True

def test_speculative_decoding_calculations(flask_client):
    """Verifies multi-model speculative decoding acceleration math and speedups."""
    response = flask_client.post(
        "/api/quantization/speculative-decoding",
        data=json.dumps({
            "acceptance_rate": 0.8,
            "draft_latency_ms": 2.0,
            "target_latency_ms": 20.0,
            "draft_steps": 5
        }),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert data["acceptance_rate_alpha"] == 0.8
    assert "expected_accepted_tokens_per_step" in data
    assert "speculative_speedup_ratio" in data
    assert data["optimal_draft_steps_k"] == 4

def test_perpetual_loop_endpoint(flask_client):
    """Verifies end-to-end continuous loop orchestration."""
    response = flask_client.post("/api/mnemosyne/perpetual-loop")
    assert response.status_code == 200
    data = response.get_json()
    assert data["loop_status"] == "RUNNING"

def test_chat_payload_validation(flask_client):
    """Ensures strict JSON body, string validation, and query logging are enforced."""
    # Missing body
    response = flask_client.post("/chat")
    assert response.status_code == 400
    assert "Malformed request" in response.get_json()["error"]

    # Missing key
    response = flask_client.post(
        "/chat",
        data=json.dumps({"msg": "hello"}),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "Missing key 'message'" in response.get_json()["error"]

    # Empty/Wrong type
    response = flask_client.post(
        "/chat",
        data=json.dumps({"message": 12345}),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "must be a non-empty string" in response.get_json()["error"]

def test_chat_blocked_codex_solomon_only(flask_client):
    """Ensures Codex actions are blocked in solomon_only mode."""
    # Set preference to solomon_only
    flask_client.post(
        "/api/command-center/preferences",
        data=json.dumps({"execution_mode": "solomon_only"}),
        content_type="application/json"
    )

    response = flask_client.post(
        "/chat",
        data=json.dumps({"message": "Hey Codex, run optimization rules please."}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "BLOCKED"
    assert "blocked because the current system preferences are set to 'solomon_only'" in data["reply"]
    assert "RECOMMENDED NEXT STEP" in data["reply"]

    # Restore preferences
    flask_client.post(
        "/api/command-center/preferences",
        data=json.dumps({"execution_mode": "hybrid"}),
        content_type="application/json"
    )

@patch("app.client")
def test_chat_live_and_fallback_modes(mock_openai_client, flask_client):
    """Verifies conversational reply and foreman routing for fallback and mock-live execution."""
    # 1. Fallback / Simulation Mode (client or api_key mock_key_if_none)
    response = flask_client.post(
        "/chat",
        data=json.dumps({"message": "Hello Solomon, let's discuss AWQ quantization."}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "GGUF" in data["reply"]
    assert "RECOMMENDED NEXT STEP" in data["reply"]
    assert "AMPBA" in data["reply"]
    assert data["worker_orchestration"] is False

    # 1b. Test alternate recommendation route for "db / mnemosyne"
    response_db = flask_client.post(
        "/chat",
        data=json.dumps({"message": "Show me our active db memory cards."}),
        content_type="application/json"
    )
    assert response_db.status_code == 200
    data_db = response_db.get_json()
    assert "search against Mnemosyne" in data_db["reply"]

    # 2. Worker Foreman Dispatcher Mode
    response_worker = flask_client.post(
        "/chat",
        data=json.dumps({"message": "Gabriel: compile codex_mcp_bridge template"}),
        content_type="application/json"
    )
    assert response_worker.status_code == 200
    data_worker = response_worker.get_json()
    assert "Foreman" in data_worker["reply"]
    assert "Gabriel" in data_worker["reply"]
    assert "READ_ONLY" in data_worker["reply"]
    assert data_worker["worker_orchestration"] is True

    # 3. Live Mock OpenAI Mode
    # Mock the response structure of client.chat.completions.create
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "This is a live-synthesized response from Solomon AI core."
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_openai_client.chat.completions.create.return_value = mock_completion

    with patch("app.api_key", "valid_test_api_key"):
        response_live = flask_client.post(
            "/chat",
            data=json.dumps({"message": "Analyze quantization limits."}),
            content_type="application/json"
        )
        assert response_live.status_code == 200
        data_live = response_live.get_json()
        assert "live-synthesized" in data_live["reply"]
        assert "RECOMMENDED NEXT STEP" in data_live["reply"]

        # Test live call throwing exception
        mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI API Outage Simulation")
        response_err = flask_client.post(
            "/chat",
            data=json.dumps({"message": "This will trigger error fallback path with Python code."}),
            content_type="application/json"
        )
        assert response_err.status_code == 200
        data_err = response_err.get_json()
        assert "LOCAL CODEX INFERENCE" in data_err["reply"]

def test_local_codex_inference_variants(flask_client):
    """Tests the diverse code-generation pathways of the LocalInferenceEngine."""
    # Test case 1: "write a Python script to test local capability"
    response1 = flask_client.post(
        "/chat",
        data=json.dumps({"message": "write a python test script"}),
        content_type="application/json"
    )
    assert response1.status_code == 200
    data1 = response1.get_json()
    assert "LOCAL CODEX INFERENCE" in data1["reply"]
    assert "test_local_capability_example" in data1["reply"]

    # Test case 2: "write a function for quantization bitweights"
    response2 = flask_client.post(
        "/chat",
        data=json.dumps({"message": "write a function for quantization bitweights"}),
        content_type="application/json"
    )
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert "LOCAL CODEX INFERENCE" in data2["reply"]
    assert "run_ampba_allocation_offline" in data2["reply"]

    # Test case 3: generic code request
    response3 = flask_client.post(
        "/chat",
        data=json.dumps({"message": "write a general capability compiled script"}),
        content_type="application/json"
    )
    assert response3.status_code == 200
    data3 = response3.get_json()
    assert "LOCAL CODEX INFERENCE" in data3["reply"]
    assert "execute_synthesized_job" in data3["reply"]
