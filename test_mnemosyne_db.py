"""
Unit and Integration Tests for Solomon Mnemosyne SQLite DB & Semantic Search Engine.
"""

import os
import json
import sqlite3
import pytest
from app import app, router
from solomon_mnemosyne_db import SolomonMnemosyneDB

@pytest.fixture
def test_db():
    db_path = "test_solomon_mnemosyne_temp.db"
    # Remove existing temp db if any
    if os.path.exists(db_path):
        os.remove(db_path)

    db = SolomonMnemosyneDB(db_path)
    yield db

    # Clean up after tests
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSolomonMnemosyneDB:
    """
    Tests for the SQLite relational card database, L2 normalized hashing embeddings,
    and cosine similarity searches with zero-division protections.
    """

    def test_database_initialization(self, test_db):
        assert os.path.exists(test_db.db_path)

        # Check initial cards retrieval (should be empty)
        cards = test_db.get_all_cards()
        assert len(cards) == 0

    def test_compute_local_embedding_l2_normalization(self, test_db):
        text = "Maintain ultra-efficient local memory footprint for edge execution."
        vector = test_db.compute_local_embedding(text)

        assert len(vector) == 128
        # Assert L2 normalized vector norm = 1.0 (approximately)
        sq_sum = sum(x ** 2 for x in vector)
        assert abs(sq_sum - 1.0) < 1e-5

    def test_compute_local_embedding_empty_text_protection(self, test_db):
        # Empty text input should return a valid normalized fallback vector without failing
        vector = test_db.compute_local_embedding("")
        assert len(vector) == 128
        sq_sum = sum(x ** 2 for x in vector)
        assert abs(sq_sum - 1.0) < 1e-5

    def test_upsert_and_retrieve_card(self, test_db):
        card_id = "SOK-TEST-CARD-999"
        family = "Mission"
        focus = "VRAM metrics"
        content = "Formulate average Hessian trace spectrums."

        assert test_db.upsert_card(card_id, family, focus, content) is True

        card = test_db.get_card(card_id)
        assert card is not None
        assert card["card_id"] == card_id
        assert card["family"] == family
        assert card["focus"] == focus
        assert card["content"] == content
        assert len(card["embedding"]) == 128
        assert card["confidence"] == 1.0

    def test_relational_directed_links(self, test_db):
        # Insert two cards
        assert test_db.upsert_card("CARD-A", "Mission", "A", "Base mission statement") is True
        assert test_db.upsert_card("CARD-B", "Procedure", "B", "Procedural step details") is True

        # Add directed link
        assert test_db.add_link("CARD-B", "CARD-A", "DEPENDS_ON") is True

        # Retrieve card to assert relationships are linked correctly
        card_b = test_db.get_card("CARD-B")
        assert len(card_b["outgoing_links"]) == 1
        assert card_b["outgoing_links"][0]["target_id"] == "CARD-A"
        assert card_b["outgoing_links"][0]["relationship_type"] == "DEPENDS_ON"

        card_a = test_db.get_card("CARD-A")
        assert len(card_a["incoming_links"]) == 1
        assert card_a["incoming_links"][0]["source_id"] == "CARD-B"
        assert card_a["incoming_links"][0]["relationship_type"] == "DEPENDS_ON"

    def test_semantic_search_cosine_similarity(self, test_db):
        # Insert diverse cards
        test_db.upsert_card("CARD-RAM", "Procedure", "RAM", "Configure VRAM limits and memory budget knapsack constraints.")
        test_db.upsert_card("CARD-WEATHER", "Procedure", "Weather", "Forecast atmospheric pressure and temperature precipitation.")

        # Search for RAM concepts
        results_ram = test_db.semantic_search("knapsack VRAM memory", top_k=5)
        assert len(results_ram) == 2
        # First result should be the RAM card with higher similarity score
        assert results_ram[0]["card_id"] == "CARD-RAM"
        assert results_ram[1]["card_id"] == "CARD-WEATHER"
        assert results_ram[0]["similarity"] > results_ram[1]["similarity"]

        # Assert capped boundary conditions
        for r in results_ram:
            assert -1.0 <= r["similarity"] <= 1.0

    def test_card_confidence_scaling(self, test_db):
        card_id = "SOK-TEST-CONF"
        test_db.upsert_card(card_id, "Procedure", "Test", "Testing confidence scaling loops.")

        # Success upgrade
        success, conf1 = test_db.update_card_confidence(card_id, "success", learning_rate=0.05)
        assert success is True
        assert conf1 == 1.05

        # Success upgrade again
        _, conf2 = test_db.update_card_confidence(card_id, "success", learning_rate=0.05)
        assert conf2 == 1.1025

        # Failure downgrade
        _, conf3 = test_db.update_card_confidence(card_id, "failure", learning_rate=0.10)
        assert abs(conf3 - (1.1025 * 0.90)) < 1e-4

        # Verify clipping upper bound [2.0]
        for _ in range(50):
            test_db.update_card_confidence(card_id, "success", learning_rate=0.20)
        card = test_db.get_card(card_id)
        assert card["confidence"] == 2.0

        # Verify clipping lower bound [0.1]
        for _ in range(50):
            test_db.update_card_confidence(card_id, "failure", learning_rate=0.20)
        card = test_db.get_card(card_id)
        assert card["confidence"] == 0.1


class TestMnemosyneAPIIntegration:
    """
    Integration tests for Flask routing endpoints.
    """

    def test_get_mnemosyne_cards(self, client):
        response = client.get("/api/mnemosyne/cards")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "cards" in data
        assert data["total_cards"] > 0

        # Check that relation details are populated
        card_procedure = data["cards"]["SOK-PROCEDURE-QUANT-001"]
        assert len(card_procedure["outgoing_links"]) > 0
        assert card_procedure["outgoing_links"][0]["target_id"] == "SOK-MISSION-QUANT-001"

    def test_search_mnemosyne_cards_success(self, client):
        payload = {
            "query": "Hessian trace and Multi-Choice Knapsack budget allocation",
            "top_k": 3
        }
        response = client.post(
            "/api/mnemosyne/search",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert len(data["results"]) > 0
        # The top result should be the Procedure card containing Hessian knapsack details
        assert data["results"][0]["card_id"] == "SOK-PROCEDURE-QUANT-001"
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_search_mnemosyne_cards_missing_param(self, client):
        payload = {
            "top_k": 5
        }
        response = client.post(
            "/api/mnemosyne/search",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_get_cognitive_cycle(self, client):
        """
        Asserts that the GET /api/quantization/cognitive-cycle endpoint returns an
        HTTP 200 status code and the correct JSON schema with fields matching the SOK card families.
        """
        response = client.get("/api/quantization/cognitive-cycle")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "active"
        assert len(data["seven_stages_sequence"]) == 7

        cards = data["sok_card_families"]
        assert cards["SOK-MISSION-QUANT-001"]["family"] == "Mission"
        assert cards["SOK-PROCEDURE-QUANT-001"]["family"] == "Procedure"
        assert cards["SOK-TASK-QUANT-001"]["family"] == "Task"
        assert cards["SOK-EXECUTION-QUANT-001"]["family"] == "Execution"
        assert cards["SOK-REVIEW-QUANT-001"]["family"] == "Review"
        assert cards["SOK-KNOWLEDGE-QUANT-001"]["family"] == "Knowledge"
        assert cards["SOK-IMPROVED-PROCEDURE-QUANT-001"]["family"] == "Improved Procedure"
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_route_mnemosyne_query_high_precision(self, client):
        """
        Asserts that querying with complex, SOK-relevant terms routes the request
        to the High-Precision Target Model.
        """
        payload = {
            "query": "Solve the multi-choice knapsack integer program with average Hessian traces",
            "threshold": 0.40
        }
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        decision = data["routing_decision"]
        assert decision["model_type"] == "high_precision"
        assert "High-Precision" in decision["routed_model"]
        assert decision["precision_allocated"] == "FP16/INT8"
        assert decision["active_ram_footprint_gb"] == 14.0
        assert decision["estimated_latency_ms"] == 55.0
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_route_mnemosyne_query_ultra_light(self, client):
        """
        Asserts that querying with standard, SOK-irrelevant terms routes the request
        to the Ultra-Light Quantized Model, checking size footprint and cost savings.
        """
        payload = {
            "query": "How to make a chocolate chip cookie dessert",
            "threshold": 0.40
        }
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        decision = data["routing_decision"]
        assert decision["model_type"] == "ultra_light"
        assert "Ultra-Light" in decision["routed_model"]
        assert decision["precision_allocated"] == "INT4/Ternary"
        assert decision["active_ram_footprint_gb"] == 0.7
        assert decision["estimated_latency_ms"] == 12.0

        # Check resource impacts
        impact = decision["resource_impact"]
        assert impact["vram_saved_gb"] == 13.3
        assert impact["latency_reduction_percent"] == 78.2
        assert impact["cost_savings_percent"] == 95.0

    def test_route_mnemosyne_query_invalid_params(self, client):
        # Trigger validation failure via missing query parameter
        payload = {"threshold": 0.15}
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_skill_factory_package_compilation(self):
        """
        Directly asserts that Gabriel's Skill Factory correctly compiles learned scripts
        into structured, modular, and testable Skill Packages.
        """
        from solomon_skill_factory import SkillFactory
        source = "def calc(): return 100"
        package = SkillFactory.compile_skill_package(
            skill_id="SKILL-CALC-001",
            name="Calculator math optimizer",
            purpose="Solves complex floating-point allocations",
            source_code=source,
            inputs_schema={"value": "float"},
            outputs_schema={"return": "float"},
            safety_constraints=["RAM <= 50MB"]
        )

        assert package["skill_id"] == "SKILL-CALC-001"
        assert package["status"] == "COMPILED"
        assert "def test_skill_calc_001():" in package["autogenerated_tests"]
        assert package["bytes_count"] == len(source)

    def test_skill_graph_navigator_sorts_and_health(self):
        """
        Directly asserts that the Skill Graph Navigator maps dependencies, sorts
        topologically, and scans call graph health to find redundancies/recommendations.
        """
        from solomon_skill_graph_navigator import SkillGraphNavigator
        nav = SkillGraphNavigator()

        # Register dependent nodes
        nav.register_skill_node("SKILL-C", "Skill C", ["SKILL-B"])
        nav.register_skill_node("SKILL-B", "Skill B", ["SKILL-A"])
        nav.register_skill_node("SKILL-A", "Skill A", [])

        # Topological sorting should output: A, B, C
        order = nav.topological_sort()
        assert order == ["SKILL-A", "SKILL-B", "SKILL-C"]

        # Health scan (should be 100% healthy, no missing vectors or redundancies)
        health = nav.analyze_graph_health()
        assert health["is_healthy"] is True
        assert len(health["missing_knowledge_vectors"]) == 0

        # Inject missing vector (dependency SKILL-X on A)
        nav.register_skill_node("SKILL-A", "Skill A", ["SKILL-X"])
        health_unhealthy = nav.analyze_graph_health()
        assert health_unhealthy["is_healthy"] is False
        assert health_unhealthy["missing_knowledge_vectors"] == ["SKILL-X"]
        assert "Learn prerequisite capability 'SKILL-X'" in health_unhealthy["next_learning_recommendations"][0]

    def test_skill_factory_and_navigator_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/skills/factory/create and GET /api/mnemosyne/skills/graph/analyze
        routes process correct payloads, register compiled packages inside the active graph,
        and calculate topological paths successfully.
        """
        # 1. POST Create Skill Package
        payload = {
            "skill_id": "SKILL-DOCKER-MONITOR-001",
            "name": "Docker CPU Probe",
            "purpose": "Reads microsecond statistics",
            "source_code": "def probe(): return 92.5",
            "prerequisites": ["SKILL-MATH-BASE-001"],
            "inputs_schema": {"container": "string"},
            "outputs_schema": {"cpu_percent": "float"}
        }
        res_create = client.post(
            "/api/mnemosyne/skills/factory/create",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res_create.status_code == 200
        data_create = res_create.get_json()
        assert data_create["status"] == "success"

        pkg = data_create["compiled_skill_package"]
        assert pkg["skill_id"] == "SKILL-DOCKER-MONITOR-001"

        # 2. GET Analyze Graph Health & Order
        res_get = client.get("/api/mnemosyne/skills/graph/analyze")
        assert res_get.status_code == 200
        data_get = res_get.get_json()
        assert data_get["status"] == "success"

        health = data_get["graph_health_report"]
        assert "SKILL-MATH-BASE-001" in health["missing_knowledge_vectors"]
        assert len(data_get["recommended_topological_execution_order"]) > 0

    def test_prometheus_curiosity_engine_scoring(self):
        """
        Directly asserts that the Prometheus Curiosity Engine calculates and sorts
        Learning Opportunities using the Opportunity Weighting Matrix correctly.
        """
        from solomon_prometheus_curiosity import PrometheusCuriosityEngine
        score = PrometheusCuriosityEngine.calculate_lo_score(10.0, 5.0, 10.0, 2.0, 2.0)
        # score = (1.5 * 10) + (1.0 * 5) + (1.2 * 10) - (0.8 * 2) - (0.5 * 2) = 15 + 5 + 12 - 1.6 - 1 = 29.4
        assert score == 29.4

        opps = PrometheusCuriosityEngine.discover_learning_opportunities({})
        assert len(opps) == 3
        # Check sorted order descending
        assert opps[0]["lo_score"] >= opps[1]["lo_score"]
        assert opps[1]["lo_score"] >= opps[2]["lo_score"]

    def test_curiosity_and_experiment_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/curiosity/discover and POST /api/mnemosyne/experiment/run
        endpoints process requests, execute the formal scientific experiment pipeline,
        and dynamically promote verified cards through the SQLite database state gates.
        """
        # 1. Trigger discover route
        res_disc = client.post("/api/mnemosyne/curiosity/discover", data=json.dumps({}), content_type="application/json")
        assert res_disc.status_code == 200
        data_disc = res_disc.get_json()
        assert data_disc["status"] == "success"
        assert len(data_disc["priority_learning_queue"]) > 0

        target_opp = data_disc["priority_learning_queue"][0]

        # 2. Trigger experiment run route
        payload_exp = {
            "opportunity": target_opp
        }
        res_exp = client.post("/api/mnemosyne/experiment/run", data=json.dumps(payload_exp), content_type="application/json")
        assert res_exp.status_code == 200
        data_exp = res_exp.get_json()
        assert data_exp["status"] == "success"

        report = data_exp["scientific_experiment_report"]
        assert report["opportunity_id"] == target_opp["id"]
        assert report["experiment_status"] == "SUCCESS"
        assert report["validation_state"] == "ACTIVE"

        traces = report["traces"]
        assert len(traces) == 5
        assert "Step 1" in traces[0]
        assert "Step 2" in traces[1]
        assert "Step 3" in traces[2]
        assert "Step 4" in traces[3]
        assert "Step 5" in traces[4]

    def test_worker_modes_get_and_post_api(self, client):
        """
        Asserts that /api/command-center/worker-modes correctly manages and toggles helper states.
        """
        # GET baseline check
        response_get = client.get("/api/command-center/worker-modes")
        assert response_get.status_code == 200
        data_get = response_get.get_json()
        assert data_get["status"] == "success"
        assert len(data_get["worker_modes"]) == 4

        # POST update mode
        payload = {
            "worker_id": "gabriel",
            "mode": "LIVE"
        }
        response_post = client.post(
            "/api/command-center/worker-modes",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response_post.status_code == 200
        data_post = response_post.get_json()
        assert data_post["status"] == "success"

        # Check update persisted
        modes = data_post["worker_modes"]
        gabriel_mode = [m for m in modes if m["worker_id"] == "gabriel"][0]
        assert gabriel_mode["mode"] == "LIVE"

        # Restore back to READ_ONLY for subsequent test isolation
        payload_restore = {"worker_id": "gabriel", "mode": "READ_ONLY"}
        client.post("/api/command-center/worker-modes", data=json.dumps(payload_restore), content_type="application/json")

    def test_perpetual_learning_loop_phase2_live_bypasses_and_phase3_auto_scans(self, client):
        """
        Verifies both Phase 2 physical commits (when in LIVE mode) and Phase 3 Automated Review Gate
        promotions with security audits.
        """
        # 1. Update Gabriel to LIVE mode to trigger Phase 2 physical commits
        payload_mode = {"worker_id": "gabriel", "mode": "LIVE"}
        client.post("/api/command-center/worker-modes", data=json.dumps(payload_mode), content_type="application/json")

        payload_loop = {
            "task": "Test Live Compilation and Physical Writing",
            "target_service": "kubernetes-cli-live-test"
        }
        response = client.post(
            "/api/mnemosyne/perpetual-loop",
            data=json.dumps(payload_loop),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        report = data["perpetual_learning_report"]
        impact = report["phase2_live_impact"]
        assert impact["active_mode"] == "LIVE"
        assert impact["physical_file_written"] is True
        assert impact["registered_in_active_graph"] is True

        review_impact = report["phase3_review_gate_impact"]
        assert review_impact["security_scan_passed"] is True
        assert review_impact["review_gate_promoted"] is True

        # Assert file was physically written to disk
        filepath = "solomon_rebuilt_kubernetes_cli_live_test.py"
        assert os.path.exists(filepath) is True

        # Clean up files from disk
        os.remove(filepath)

        # Restore worker mode back to READ_ONLY
        payload_restore = {"worker_id": "gabriel", "mode": "READ_ONLY"}
        client.post("/api/command-center/worker-modes", data=json.dumps(payload_restore), content_type="application/json")

        # Trigger validation failure via non-numeric threshold parameter
        payload = {"query": "test query", "threshold": "invalid_threshold"}
        response = client.post(
            "/api/mnemosyne/route",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_feedback_and_self_healing_routing_loop(self, client):
        """
        Verifies the complete reinforcement loop:
        1. Query initially routes to Ultra-Light because similarity is low (< threshold).
        2. SOK card receives 'failure' feedback, driving its confidence score down.
        3. Subsequent Model Router queries dynamically lower the effective threshold,
           forcing self-healing routing of future matches to the High-Precision Target Model.
        """
        card_id = "SOK-MISSION-QUANT-001"
        query_text = "VRAM metrics during high-throughput edge execution"

        # Robustly Reset the active database card's confidence score to exactly 1.0 before test run
        conn = sqlite3.connect("solomon_mnemosyne_demo.db")
        conn.execute("UPDATE knowledge_cards SET confidence = 1.0 WHERE card_id = ?", (card_id,))
        conn.commit()
        conn.close()

        # Baseline check: Query gets similarity of ~0.41, routed to ultra-light with threshold 0.60
        # Set base threshold to be higher than similarity (0.4143) to ensure it is ultra-light
        payload_route = {
            "query": query_text,
            "threshold": 0.60
        }
        res1 = client.post("/api/mnemosyne/route", data=json.dumps(payload_route), content_type="application/json")
        assert res1.status_code == 200
        assert res1.get_json()["routing_decision"]["model_type"] == "ultra_light"

        # Send failure feedback to drive card confidence down to 0.50 (learning rate 0.50)
        payload_feedback = {
            "card_id": card_id,
            "outcome": "failure",
            "learning_rate": 0.50
        }
        res_feedback = client.post("/api/mnemosyne/feedback", data=json.dumps(payload_feedback), content_type="application/json")
        assert res_feedback.status_code == 200
        assert res_feedback.get_json()["new_card_confidence"] == 0.50

        # Run route query again: effective threshold = 0.60 * 0.50 = 0.30.
        # Max similarity (~0.41) is now >= effective threshold (0.30), forcing high-precision self-healing!
        res2 = client.post("/api/mnemosyne/route", data=json.dumps(payload_route), content_type="application/json")
        assert res2.status_code == 200
        decision = res2.get_json()["routing_decision"]
        assert decision["model_type"] == "high_precision"
        assert decision["best_match_confidence"] == 0.50
        assert decision["effective_threshold"] == 0.30

        # Clean up database confidence state back to 1.0 for subsequent test isolation
        conn = sqlite3.connect("solomon_mnemosyne_demo.db")
        conn.execute("UPDATE knowledge_cards SET confidence = 1.0 WHERE card_id = ?", (card_id,))
        conn.commit()
        conn.close()

    def test_recursive_crucible_telemetry_trigger(self, client):
        """
        Verifies that POST /api/mnemosyne/crucible successfully analyzes telemetry,
        triggers corresponding AST optimizations (fusion, prune, safety), and returns HTTP 200.
        """
        # Test 1: Latency exceeds threshold -> AST-FUSION
        payload = {
            "latency_ms": 65.0,
            "rss_memory_mb": 1200.0,
            "failure_rate": 0.02
        }
        response = client.post("/api/mnemosyne/crucible", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        rep = data["recursive_crucible_report"]
        assert "AST-FUSION" in rep["crucible_actions_triggered"][0]
        assert rep["crucible_metrics"]["projected_throughput_speedup"] == 1.35
        assert rep["crucible_metrics"]["projected_ram_savings_percent"] == 0.0

        # Test 2: RAM pressure exceeds limits -> AST-PRUNE
        payload_ram = {
            "latency_ms": 30.0,
            "rss_memory_mb": 1600.0,
            "failure_rate": 0.02
        }
        res_ram = client.post("/api/mnemosyne/crucible", data=json.dumps(payload_ram), content_type="application/json")
        assert res_ram.status_code == 200
        rep_ram = res_ram.get_json()["recursive_crucible_report"]
        assert "AST-PRUNE" in rep_ram["crucible_actions_triggered"][0]
        assert rep_ram["crucible_metrics"]["projected_ram_savings_percent"] == 32.4

        # Test 3: Failure rate is high -> AST-SAFETY
        payload_fail = {
            "latency_ms": 25.0,
            "rss_memory_mb": 1100.0,
            "failure_rate": 0.12
        }
        res_fail = client.post("/api/mnemosyne/crucible", data=json.dumps(payload_fail), content_type="application/json")
        assert res_fail.status_code == 200
        rep_fail = res_fail.get_json()["recursive_crucible_report"]
        assert "AST-SAFETY" in rep_fail["crucible_actions_triggered"][0]
        assert rep_fail["crucible_metrics"]["projected_failure_reduction_percent"] == 92.0
        assert "RECOMMENDED NEXT STEP" in res_fail.get_json()["recommended_next_step"]

    def test_dynamic_ast_injection_endpoint(self, client):
        """
        Verifies that POST /api/mnemosyne/ast-inject successfully parses AST,
        injects a new method, hot-reloads the module, and allows in-memory
        execution of the newly injected function successfully with zero downtime.
        """
        payload = {
            "class_name": "ModelRouter",
            "method_name": "injected_telemetry_probe",
            "source_code": "def injected_telemetry_probe(self):\n    return 'ast_injection_active_soss'"
        }
        response = client.post("/api/mnemosyne/ast-inject", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["injected_method_name"] == "injected_telemetry_probe"
        assert data["module_hot_reloaded"] == "solomon_model_router"

        # Access reloaded global router in app and execute newly injected method
        from app import router as reloaded_router
        assert hasattr(reloaded_router, "injected_telemetry_probe") is True
        assert reloaded_router.injected_telemetry_probe() == "ast_injection_active_soss"

    def test_observational_binary_profiling_endpoint(self, client):
        """
        Verifies that POST /api/mnemosyne/observe successfully profiles execution
        bytes and programmatically synthesizes a clean-room Python equivalent successfully.
        """
        payload = {
            "binary_name": "kubernetes-cli",
            "command": "get nodes",
            "std_output": "NAME STATUS ROLES AGE VERSION\nnode1 Ready control-plane 15d v1.28"
        }
        response = client.post("/api/mnemosyne/observe", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        rep = data["rebuilt_binary_report"]
        assert rep["status"] == "binary_assimilated"

        details = rep["compilation_details"]
        assert details["binary_profiled"] == "kubernetes-cli"
        assert details["clean_room_class_synthesized"] == "SolomonRebuiltKubernetesCli"
        assert details["clean_room_method_name"] == "run"
        assert details["original_dependency_removed"] is True

        assert "class SolomonRebuiltKubernetesCli" in rep["synthesized_source_code"]
        assert "def run(self, *args, **kwargs)" in rep["synthesized_source_code"]
        assert "node1 Ready control-plane" in rep["synthesized_source_code"]
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_get_sandbox_skills_list(self, client):
        """
        Verifies GET /api/mnemosyne/skills returns registered capability nodes.
        """
        response = client.get("/api/mnemosyne/skills")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["total_skills"] > 0
        assert data["skills"][0]["skill_id"] == "SKILL-ARRAY-SORT-001"

    def test_execute_sandbox_skill_optimizer_success(self, client):
        """
        Verifies POST /api/mnemosyne/skills/execute successfully runs quicksort
        under quarantined sandbox execution subprocess environment.
        """
        payload = {
            "skill_id": "SKILL-ARRAY-SORT-001",
            "args": [[31, 4, 15, 92, 65, 35, 89]],
            "timeout_sec": 3.0
        }
        response = client.post("/api/mnemosyne/skills/execute", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["skill_name"] == "Quicksort Array Optimizer"

        sandbox = data["sandboxed_execution_result"]
        assert sandbox["success"] is True
        assert sandbox["return_value"] == [4, 15, 31, 35, 65, 89, 92]
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_execute_sandbox_skill_timeout_interception(self, client):
        """
        Verifies POST /api/mnemosyne/skills/execute captures and halts infinite loop
        subprocesses cleanly under timeout boundaries, preserving parent process health.
        """
        payload = {
            "skill_id": "SKILL-DIB-001",
            "timeout_sec": 0.5 # strict timeout
        }
        response = client.post("/api/mnemosyne/skills/execute", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        sandbox = data["sandboxed_execution_result"]
        assert sandbox["success"] is False
        assert "TimeoutExpired" in sandbox["error"] or "timeout" in sandbox["error"]
        assert "prevented" in sandbox["error"] or "killed" in sandbox["error"]

    def test_perpetual_learning_loop_end_to_end_cycle(self, client):
        """
        Verifies the complete 7-stage perpetual learning cycle via POST /api/mnemosyne/perpetual-loop.
        Assimilates a mock service, transitions through the Review Gate (DRAFT -> REVIEWED -> APPROVED -> ACTIVE),
        verifies model router retrieval, and asserts resource efficiency metrics.
        """
        payload = {
            "task": "Test Core Perpetual Learning Cycle",
            "target_service": "kubernetes-cli-mock"
        }
        response = client.post(
            "/api/mnemosyne/perpetual-loop",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        report = data["perpetual_learning_report"]
        assert report["task"] == "Test Core Perpetual Learning Cycle"
        assert report["target_service"] == "kubernetes-cli-mock"
        assert report["validation_gate_final_state"] == "ACTIVE"
        assert report["reinforced_card_confidence"] == 1.10

        efficiency = report["resource_efficiency_metrics"]
        assert efficiency["vram_saved_gb"] == 13.3
        assert efficiency["latency_reduction_percent"] == 78.2
        assert efficiency["cost_savings_percent"] == 95.0

        traces = report["cognitive_execution_traces"]
        assert len(traces) > 0
        assert "Stage 1 & 2" in traces[0]
        assert "Review Gate" in traces[3] or "Phase 3" in traces[3]
        assert "Stage 5 & 6" in traces[-1]
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_update_validation_state_success_and_failure(self, test_db):
        card_id = "SOK-TEST-VALID-STATE"
        # Test updating a non-existent card (should fail)
        assert test_db.update_card_validation_state("SOK-NON-EXISTENT", "ACTIVE") is False

        # Test updating an existing card
        test_db.upsert_card(card_id, "Procedure", "Test focus", "Test content", "DRAFT")
        assert test_db.get_card(card_id)["validation_state"] == "DRAFT"

        # Transit to REVIEWED
        assert test_db.update_card_validation_state(card_id, "REVIEWED") is True
        assert test_db.get_card(card_id)["validation_state"] == "REVIEWED"

        # Transit to APPROVED
        assert test_db.update_card_validation_state(card_id, "APPROVED") is True
        assert test_db.get_card(card_id)["validation_state"] == "APPROVED"

        # Transit to ACTIVE
        assert test_db.update_card_validation_state(card_id, "ACTIVE") is True
        assert test_db.get_card(card_id)["validation_state"] == "ACTIVE"

    def test_docker_sandbox_executor_direct(self):
        """
        Directly asserts that DockerSandboxExecutor executes code safely and uses its
        exception-resilient SandboxExecutor subprocess fallback in nested storage conditions.
        """
        from solomon_docker_executor import DockerSandboxExecutor
        source = (
            "def add_nums(a, b):\n"
            "    return a + b\n"
        )
        res = DockerSandboxExecutor.execute_in_container(source, "add_nums(10, 32)", timeout_sec=2.0)
        assert res["success"] is True
        assert res["return_value"] == 42
        assert "fallback" in res["message"] or "Quarantined" in res["message"]

    def test_docker_sandbox_api_route(self, client):
        """
        Verifies POST /api/mnemosyne/docker/execute processes correct payload, triggers
        the Docker execution lane, and returns the correct success JSON response schema.
        """
        payload = {
            "source_code": "def run_multiply(x, y):\n    return x * y\n",
            "entry_call": "run_multiply(7, 8)",
            "timeout_sec": 3.0
        }
        response = client.post(
            "/api/mnemosyne/docker/execute",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        sandbox_res = data["docker_sandbox_result"]
        assert sandbox_res["success"] is True
        assert sandbox_res["return_value"] == 56
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_docker_sandbox_api_invalid_payload(self, client):
        """
        Asserts that calling the endpoint with missing or malformed values returns HTTP 400.
        """
        # Missing source_code
        payload = {"entry_call": "test()"}
        response = client.post(
            "/api/mnemosyne/docker/execute",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        assert "error" in response.get_json()
