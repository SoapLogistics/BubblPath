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
    """Verifies SOK sequence steps and active card families retrieval."""
    response = flask_client.get("/api/quantization/cognitive-cycle")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["cycle_stages"]) == 7
    assert "Observe" in data["cycle_stages"][0]
    assert "Memory Efficiency" in data["active_card_families"]
    assert data["is_integrated_blueprint"] is True

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
    """Verifies mock local 128-dimensional fallback semantic search rankings and cosine boundaries."""
    response = flask_client.post(
        "/api/mnemosyne/search",
        data=json.dumps({"query": "Ternary SpinQuant optimization"}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert len(data["results"]) >= 1
    # Check that cosine boundaries division-by-zero protection holds strictly inside [-1.0, 1.0]
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

def test_sandbox_hard_timeout_guard(flask_client):
    """Verifies that Prometheus hard-timeout subprocess constraints terminate runaway loops successfully."""
    # POST execution with a runaway loop and custom timeout limit of 1.0 second
    runaway_code = (
        "import time\n"
        "while True:\n"
        "    time.sleep(0.1)\n"
    )
    response = flask_client.post(
        "/api/mnemosyne/skills/execute",
        data=json.dumps({
            "skill_id": "jules_endless_runaway",
            "code": runaway_code,
            "timeout_seconds": 1.0
        }),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["execution_status"] == "TIMEOUT"
    assert data["exit_code"] == -1
    assert "TimeoutExpired" in data["stderr"]
    assert "Runaway process terminated" in data["stderr"]

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

def test_directed_linkage_blocker_traversal(flask_client):
    """Verifies recursive traversal detection of multi-layer PREVENTS execution linkage blockers."""
    # Linkage setup:
    # Node 1 -> Node 3 is ENHANCES (Not a blocker)
    # Node 3 -> Node 2 is PREVENTS relationship blocker
    flask_client.post(
        "/api/mnemosyne/cards/links",
        data=json.dumps({"source_id": 1, "target_id": 3, "relationship_type": "ENHANCES"}),
        content_type="application/json"
    )
    flask_client.post(
        "/api/mnemosyne/cards/links",
        data=json.dumps({"source_id": 3, "target_id": 2, "relationship_type": "PREVENTS"}),
        content_type="application/json"
    )

    # 1. Validation check (missing keys)
    response_val = flask_client.post(
        "/api/mnemosyne/cards/links/traversal",
        data=json.dumps({"source_id": 1}),
        content_type="application/json"
    )
    assert response_val.status_code == 400

    # 2. Assert multi-layer block detection (1 -> 3 -> 2 contains PREVENTS blocker)
    response_block = flask_client.post(
        "/api/mnemosyne/cards/links/traversal",
        data=json.dumps({"source_id": 1, "target_id": 2}),
        content_type="application/json"
    )
    assert response_block.status_code == 200
    assert response_block.get_json()["blocked"] is True

    # 3. Assert direct blocker detection (3 -> 2 contains PREVENTS blocker)
    response_direct = flask_client.post(
        "/api/mnemosyne/cards/links/traversal",
        data=json.dumps({"source_id": 3, "target_id": 2}),
        content_type="application/json"
    )
    assert response_direct.status_code == 200
    assert response_direct.get_json()["blocked"] is True

    # 4. Assert clean non-blocking route (1 -> 1)
    response_clean = flask_client.post(
        "/api/mnemosyne/cards/links/traversal",
        data=json.dumps({"source_id": 1, "target_id": 1}),
        content_type="application/json"
    )
    assert response_clean.status_code == 200
    assert response_clean.get_json()["blocked"] is False

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

def test_gguf_modelfile_compiler(flask_client):
    """Verifies GGUF Modelfile compiler parameter outputs and terminal instructions."""
    response = flask_client.post(
        "/api/command-center/quantization/compile-calibration",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert "FROM ./models/llama-3-8b-fp16.gguf" in data["compiled_modelfile"]
    assert "llama-quantize" in data["execution_instructions_command_line"]
    assert "ollama create" in data["ollama_creation_command_line"]

def test_unified_closed_loop_perpetual_orchestrator(flask_client):
    """Verifies the unified 7-stage closed-loop perpetual learning sequence orchestrations."""
    response = flask_client.post(
        "/api/mnemosyne/perpetual-loop",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["loop_status"] == "SUCCESS_CLOSED_LOOP"
    assert "Observe -> Learn -> Remember -> Retrieve -> Improve" in data["sequence_stages"]
    assert data["sandbox_execution_status"] == "SUCCESS"
    assert "remembered_new_card_inserted" in data
    assert data["retrieved_total_cards_count"] >= 4

def test_context_budgeting_compression(flask_client):
    """Verifies that conversation history exceeding 10,000 characters triggers active context compression."""
    long_msg = "A" * 10500 # Over 10k character limit
    response = flask_client.post(
        "/chat",
        data=json.dumps({"message": long_msg}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["context_budget_compressed"] is True
    assert "compressed to fit within SOSS memory limits" in data["reply"]

def test_workspace_ui_sync_routes(flask_client):
    """Verifies the HTML/CSS workspace console and Project Loki picks API."""
    # 1. GET HTML Workspace Panel
    response_html = flask_client.get("/workspace")
    assert response_html.status_code == 200
    assert b"Solomon Cognitive" in response_html.data
    assert b"Loki Sports Betting" in response_html.data

    # 2. GET Loki Picks API
    response_picks = flask_client.get("/api/picks")
    assert response_picks.status_code == 200
    data_picks = response_picks.get_json()
    assert data_picks["status"] == "SUCCESS"
    assert len(data_picks["picks"]) == 3
    assert data_picks["picks"][0]["sport"] == "NFL"

def test_startup_pipeline_initialization(flask_client):
    """Verifies the start-up mixed-precision layer-by-layer bit-allocation map metrics."""
    response = flask_client.get("/api/mnemosyne/startup-pipeline")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert data["total_layers"] == 32
    assert len(data["layers"]) == 32
    assert "allocated_bitwidth" in data["layers"][0]
    assert 2.0 <= data["average_allocated_bit_width"] <= 8.0

def test_visual_graph_pipeline(flask_client):
    """Verifies topological card graph density metrics and visual layout coordinate allocations."""
    response = flask_client.get("/api/mnemosyne/cards/graph/visual")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SUCCESS"
    assert "density_metrics" in data
    assert "visual_graph" in data
    assert data["density_metrics"]["node_count"] >= 3
    assert data["visual_graph"]["nodes"][0]["x"] is not None

def test_multi_agent_planner_draft_and_execution(flask_client):
    """Verifies high-level multi-step planner drafts and automatic code execution promotions."""
    # 1. Planner Draft Failure check (Missing key)
    res_val = flask_client.post(
        "/api/command-center/planner/draft",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert res_val.status_code == 400

    # 2. Successful Planner Draft
    res_draft = flask_client.post(
        "/api/command-center/planner/draft",
        data=json.dumps({"prompt": "Construct a dynamic offloading GCPP module"}),
        content_type="application/json"
    )
    assert res_draft.status_code == 201
    draft_data = res_draft.get_json()
    assert draft_data["status"] == "SUCCESS"
    assert len(draft_data["drafted_task_pipeline"]) == 4
    assert draft_data["created_draft_card"]["status"] == "DRAFT"

    # 3. Successful Planner Execute & Promotion
    run_code = (
        "import sys\n"
        "sys.stdout.write('Planner compiled dynamic code successfully')\n"
        "sys.exit(0)\n"
    )
    res_exec = flask_client.post(
        "/api/command-center/planner/execute",
        data=json.dumps({"skill_id": "dynamic_planner_runner", "code": run_code}),
        content_type="application/json"
    )
    assert res_exec.status_code == 200
    exec_data = res_exec.get_json()
    assert exec_data["status"] == "SUCCESS"
    assert exec_data["prometheus_audit_status"] == "PASSED"
    assert exec_data["promoted_to_active"] is True

    # 4. Check active memory card was promoted
    res_check = flask_client.get("/api/mnemosyne/cards?status=ACTIVE")
    active_cards = res_check.get_json()
    promoted = [c for c in active_cards if "dynamic_planner_runner" in c["title"]]
    assert len(promoted) == 1

def test_perpetual_loop_endpoint(flask_client):
    """Verifies end-to-end continuous loop orchestration."""
    response = flask_client.post("/api/mnemosyne/perpetual-loop")
    assert response.status_code == 200
    data = response.get_json()
    assert data["loop_status"] == "SUCCESS_CLOSED_LOOP"

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

def test_tensor_coherence_optimizer(flask_client):
    """Verifies Phase XXX quantum-inspired tensor coherence metrics calculations and error payloads."""
    # 1. Missing payload key
    res_err1 = flask_client.post("/api/quantization/tensor-coherence", data=json.dumps({}), content_type="application/json")
    assert res_err1.status_code == 400
    assert "Missing key 'tensors'" in res_err1.get_json()["error"]

    # 2. Invalid parameter type
    res_err2 = flask_client.post("/api/quantization/tensor-coherence", data=json.dumps({"tensors": "not-a-list"}), content_type="application/json")
    assert res_err2.status_code == 400
    assert "Argument 'tensors' must be a list" in res_err2.get_json()["error"]

    # 3. Successful calculation with empty/undefined angles (coherence default 1.0)
    res_empty_angles = flask_client.post(
        "/api/quantization/tensor-coherence",
        data=json.dumps({"tensors": [{"tensor_id": "layer_1_weight", "dimension": 256}]}),
        content_type="application/json"
    )
    assert res_empty_angles.status_code == 200
    data_empty = res_empty_angles.get_json()
    assert data_empty["status"] == "SUCCESS"
    assert data_empty["average_system_coherence"] == 1.0
    assert data_empty["coherence_stable"] is True

    # 4. Successful math calculation with given phase angles
    res_math = flask_client.post(
        "/api/quantization/tensor-coherence",
        data=json.dumps({"tensors": [
            {
                "tensor_id": "layer_1_activation",
                "dimension": 128,
                "phase_angles": [0.0, 0.0, 0.0]  # fully coherent (cos=1, sin=0 -> coherence=1.0)
            },
            {
                "tensor_id": "layer_2_activation",
                "dimension": 128,
                "phase_angles": [0.0, 3.1415926535]  # anti-phase (cos=1 + cos(-1) = 0 -> coherence=0.0)
            }
        ]}),
        content_type="application/json"
    )
    assert res_math.status_code == 200
    data_math = res_math.get_json()
    assert data_math["status"] == "SUCCESS"
    assert data_math["average_system_coherence"] == 0.5  # average of 1.0 and 0.0
    assert data_math["coherence_stable"] is False
    assert data_math["optimized_scaling_factors"] == [1.0, 10.0]

def test_agent_consensus_protocol(flask_client):
    """Verifies Phase XXXI Byzantine-tolerant consensus supermajority checks and vote aggregations."""
    # 1. Missing payload key
    res_err1 = flask_client.post("/api/command-center/consensus/vote", data=json.dumps({}), content_type="application/json")
    assert res_err1.status_code == 400
    assert "Missing key 'capability_id'" in res_err1.get_json()["error"]

    # 2. Invalid parameter type
    res_err2 = flask_client.post("/api/command-center/consensus/vote", data=json.dumps({"capability_id": "calc", "votes": "not-a-dict"}), content_type="application/json")
    assert res_err2.status_code == 400
    assert "Argument 'votes' must be a JSON dictionary object" in res_err2.get_json()["error"]

    # 3. Blocked promotion (below supermajority of 0.66)
    res_blocked = flask_client.post(
        "/api/command-center/consensus/vote",
        data=json.dumps({
            "capability_id": "untested_mcp_bridge",
            "votes": {
                "Gabriel": {"approved": True, "score": 0.5},
                "Mnemosyne": {"approved": False, "score": 0.0}
            }
        }),
        content_type="application/json"
    )
    assert res_blocked.status_code == 200
    data_blocked = res_blocked.get_json()
    assert data_blocked["status"] == "BLOCKED"
    assert data_blocked["consensus_authorized"] is False
    assert data_blocked["weighted_consensus_score"] < 0.66

    # 4. Authorized promotion (above supermajority of 0.66)
    res_authorized = flask_client.post(
        "/api/command-center/consensus/vote",
        data=json.dumps({
            "capability_id": "secure_parallel_worktrees",
            "votes": {
                "Gabriel": {"approved": True, "score": 0.9},
                "Mnemosyne": {"approved": True, "score": 0.85},
                "Prometheus": {"approved": True, "score": 0.95},
                "Loki": {"approved": True, "score": 0.8},
                "Codex": {"approved": True, "score": 0.9}
            }
        }),
        content_type="application/json"
    )
    assert res_authorized.status_code == 200
    data_authorized = res_authorized.get_json()
    assert data_authorized["status"] == "AUTHORIZED"
    assert data_authorized["consensus_authorized"] is True
    assert data_authorized["weighted_consensus_score"] >= 0.8

def test_ternary_entropy_regularizer(flask_client):
    """Verifies Phase XXXII ternary-weight entropy and threshold calculations with edge cases."""
    # 1. Missing payload key
    res_err1 = flask_client.post("/api/quantization/ternary-entropy", data=json.dumps({}), content_type="application/json")
    assert res_err1.status_code == 400
    assert "Missing key 'weights'" in res_err1.get_json()["error"]

    # 2. Invalid non-empty list of float values
    res_err2 = flask_client.post("/api/quantization/ternary-entropy", data=json.dumps({"weights": "not-a-list"}), content_type="application/json")
    assert res_err2.status_code == 400
    assert "must be a non-empty list" in res_err2.get_json()["error"]

    # 3. Non-numerical float list values
    res_err3 = flask_client.post("/api/quantization/ternary-entropy", data=json.dumps({"weights": ["a", "b"]}), content_type="application/json")
    assert res_err3.status_code == 400
    assert "must be numerical float values" in res_err3.get_json()["error"]

    # 4. Successful ternary mappings and Shannon entropy calculations
    res_success = flask_client.post(
        "/api/quantization/ternary-entropy",
        data=json.dumps({"weights": [0.1, -0.8, 1.2, 0.05, -0.01, 1.5, -1.1]}),
        content_type="application/json"
    )
    assert res_success.status_code == 200
    data = res_success.get_json()
    assert data["status"] == "SUCCESS"
    assert "clipping_threshold_delta" in data
    assert "shannon_entropy_bits" in data
    assert "mapped_ternary_states" in data
    assert isinstance(data["state_counts"], dict)
    assert sum(data["state_counts"].values()) == 7

def test_kv_cache_compressor(flask_client):
    """Verifies Phase XXXIII dynamic KV Cache compression and eviction rules."""
    # 1. Missing payload key
    res_err1 = flask_client.post("/api/quantization/kv-cache/compress", data=json.dumps({}), content_type="application/json")
    assert res_err1.status_code == 400
    assert "Missing key 'blocks'" in res_err1.get_json()["error"]

    # 2. Invalid block parameter type
    res_err2 = flask_client.post("/api/quantization/kv-cache/compress", data=json.dumps({"blocks": "not-a-list"}), content_type="application/json")
    assert res_err2.status_code == 400
    assert "must be a list of block objects" in res_err2.get_json()["error"]

    # 3. Eviction and compression rules mapping based on attention score
    res_success = flask_client.post(
        "/api/quantization/kv-cache/compress",
        data=json.dumps({
            "target_compression_ratio": 0.5,
            "blocks": [
                {
                    "block_id": 101,
                    "token_count": 16,
                    "attention_scores": [0.9, 0.85, 0.95]  # High attention -> RETAIN_FP16
                },
                {
                    "block_id": 102,
                    "token_count": 16,
                    "attention_scores": [0.5, 0.45, 0.55]  # Moderate attention -> COMPRESS_FP8
                },
                {
                    "block_id": 103,
                    "token_count": 16,
                    "attention_scores": [0.1, 0.2, 0.05]   # Low attention -> EVICT_INT4
                }
            ]
        }),
        content_type="application/json"
    )
    assert res_success.status_code == 200
    data = res_success.get_json()
    assert data["status"] == "SUCCESS"
    assert data["total_original_bytes"] == 16 * 128 * 2 * 3
    assert data["total_reclaimed_bytes"] > 0
    assert "reclaimed_percentage" in data

    # Assert action taken mapping
    block_actions = {b["block_id"]: b["action_taken"] for b in data["blocks"]}
    assert block_actions[101] == "RETAIN_FP16"
    assert block_actions[102] == "COMPRESS_FP8"
    assert block_actions[103] == "EVICT_INT4"

def test_spinquant_rotations(flask_client):
    """Verifies Phase XXXIV Walsh-Hadamard orthogonal rotation matrix spreads activations cleanly."""
    # 1. Missing payload key
    res_err1 = flask_client.post("/api/quantization/spinquant/rotate", data=json.dumps({}), content_type="application/json")
    assert res_err1.status_code == 400
    assert "Missing key 'activations'" in res_err1.get_json()["error"]

    # 2. Invalid parameter type
    res_err2 = flask_client.post("/api/quantization/spinquant/rotate", data=json.dumps({"activations": "not-a-list"}), content_type="application/json")
    assert res_err2.status_code == 400
    assert "must be a non-empty list of numerical values" in res_err2.get_json()["error"]

    # 3. Non-numerical values list
    res_err3 = flask_client.post("/api/quantization/spinquant/rotate", data=json.dumps({"activations": [1.0, "bad"]}), content_type="application/json")
    assert res_err3.status_code == 400
    assert "must be numerical float values" in res_err3.get_json()["error"]

    # 4. Successful rotation with outlier spreading checks
    res_success = flask_client.post(
        "/api/quantization/spinquant/rotate",
        data=json.dumps({"activations": [10.0, -1.0, 0.5, -0.5]}),
        content_type="application/json"
    )
    assert res_success.status_code == 200
    data = res_success.get_json()
    assert data["status"] == "SUCCESS"
    assert data["original_max_outlier"] == 10.0
    assert data["rotated_max_outlier"] < 10.0  # Spun outlier channel peak should be reduced
    assert data["outlier_reduction_ratio"] > 1.0
    assert len(data["rotated_activations"]) == 4

def test_qat_distillation(flask_client):
    """Verifies Phase XXXV layer-wise QAT temperature-scaled logit KL-Divergence measurements."""
    # 1. Missing payload keys
    res_err1 = flask_client.post("/api/quantization/qat/distill", data=json.dumps({"teacher_logits": [1.0]}), content_type="application/json")
    assert res_err1.status_code == 400
    assert "Missing key 'teacher_logits' or 'student_logits'" in res_err1.get_json()["error"]

    # 2. Invalid parameter types
    res_err2 = flask_client.post("/api/quantization/qat/distill", data=json.dumps({"teacher_logits": [1.0], "student_logits": "not-a-list"}), content_type="application/json")
    assert res_err2.status_code == 400
    assert "must be list objects" in res_err2.get_json()["error"]

    # 3. Size mismatch
    res_err3 = flask_client.post("/api/quantization/qat/distill", data=json.dumps({"teacher_logits": [1.0], "student_logits": [1.0, 2.0]}), content_type="application/json")
    assert res_err3.status_code == 400
    assert "must be non-empty and of identical lengths" in res_err3.get_json()["error"]

    # 4. Non-numerical elements
    res_err4 = flask_client.post("/api/quantization/qat/distill", data=json.dumps({"teacher_logits": ["bad"], "student_logits": [1.0]}), content_type="application/json")
    assert res_err4.status_code == 400
    assert "must be numerical float values" in res_err4.get_json()["error"]

    # 5. Successful KL-Divergence loss calculation
    res_success = flask_client.post(
        "/api/quantization/qat/distill",
        data=json.dumps({
            "teacher_logits": [2.0, 1.0, 0.1],
            "student_logits": [1.8, 1.1, 0.15],
            "temperature": 1.5
        }),
        content_type="application/json"
    )
    assert res_success.status_code == 200
    data = res_success.get_json()
    assert data["status"] == "SUCCESS"
    assert data["temperature"] == 1.5
    assert data["kl_divergence_loss"] >= 0.0
    assert len(data["teacher_probabilities"]) == 3
    assert len(data["student_probabilities"]) == 3
    assert "recommended_student_scaling_adjust" in data
