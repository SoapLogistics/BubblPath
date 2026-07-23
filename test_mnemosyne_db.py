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

    def test_adaptive_patching_direct(self):
        """
        Directly asserts that AdaptivePatchingEngine backs up stable file templates,
        verifies syntaxes, and programmatically restores corrupted files successfully.
        """
        from solomon_adaptive_patching import AdaptivePatchingEngine
        import os

        # Create a mock capability file
        test_file = "mock_capability_file.py"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("def func(): return 1\n")

        patcher = AdaptivePatchingEngine("test_backup_dir")
        assert patcher.backup_file(test_file) is True

        # Verify healthy
        res1 = patcher.verify_and_patch_file(test_file)
        assert res1["success"] is True
        assert res1["status"] == "HEALTHY"

        # Corrupt file
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("def corrupt_func():\n    return 1 +\n") # Syntax error

        # Verify and patch -> Should restore back to healthy!
        res2 = patcher.verify_and_patch_file(test_file)
        assert res2["success"] is True
        assert res2["status"] == "PATCHED_AND_RESTORED"

        # Check syntax was repaired
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def func(): return 1" in content

        # Clean up files
        if os.path.exists(test_file):
            os.remove(test_file)
        shutil_backup = os.path.join("test_backup_dir", test_file)
        if os.path.exists(shutil_backup):
            os.remove(shutil_backup)
        if os.path.exists("test_backup_dir"):
            os.rmdir("test_backup_dir")

    def test_collaborative_rag_sync_direct(self, test_db):
        """
        Directly asserts that CollaborativeRAGSync exports local card catalogs
        and merges peer node card and link deltas securely.
        """
        from solomon_collaborative_sync import CollaborativeRAGSync
        sync = CollaborativeRAGSync(test_db)

        # Ingest a card to export
        test_db.upsert_card("SOK-LOCAL-EXPORT", "Knowledge", "Focus", "Content block", "ACTIVE")
        catalog_json = sync.export_local_sok_catalog()

        assert "SOK-LOCAL-EXPORT" in catalog_json

        # Modify card confidence in peer catalog
        import json
        peer_data = json.loads(catalog_json)
        peer_data[0]["confidence"] = 1.95
        peer_data[0]["content"] = "Updated collaborative content."
        peer_data[0]["outgoing_links"] = [{"target_id": "SOK-TARGET-collab-01", "relationship_type": "ENHANCES"}]
        peer_catalog = json.dumps(peer_data)

        # Merge peer catalog
        res_merge = sync.import_and_merge_peer_catalog(peer_catalog)
        assert res_merge["success"] is True
        assert res_merge["cards_merged"] == 1

        # Check merged cards
        merged_card = test_db.get_card("SOK-LOCAL-EXPORT")
        assert merged_card["content"] == "Updated collaborative content."
        assert merged_card["confidence"] == 1.95

    def test_adaptive_patching_and_collab_sync_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/patching/verify and POST /api/mnemosyne/collaborative/sync
        endpoints process requests, audit capabilities, and merge catalogs successfully.
        """
        # Create a mock capability file
        test_file = "api_mock_capability.py"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("x = 10\n")

        # 1. POST Patching Verify
        payload_patch = {"filepath": test_file}
        response_patch = client.post(
            "/api/mnemosyne/patching/verify",
            data=json.dumps(payload_patch),
            content_type="application/json"
        )
        assert response_patch.status_code == 200
        data_patch = response_patch.get_json()
        assert data_patch["status"] == "success"
        assert data_patch["adaptive_patching_report"]["status"] == "HEALTHY"

        if os.path.exists(test_file):
            os.remove(test_file)

        # 2. POST Collaborative Sync
        res_collab = client.post(
            "/api/mnemosyne/collaborative/sync",
            data=json.dumps({}), # Uses default sync catalog sample
            content_type="application/json"
        )
        assert res_collab.status_code == 200
        data_collab = res_collab.get_json()
        assert data_collab["status"] == "success"
        assert data_collab["collaborative_sync_report"]["success"] is True

    def test_self_audit_probes_direct(self, test_db):
        """
        Directly asserts that SelfAuditProbes successfully runs SQLite integrity audits
        and calculates a valid Semantic Drift Ratio (SDR) of the database memory.
        """
        from solomon_self_audit_probes import SelfAuditProbes
        probes = SelfAuditProbes(test_db.db_path)

        # SQLite integrity
        integrity = probes.run_sqlite_integrity_check()
        assert integrity["status"] == "HEALTHY"
        assert integrity["integrity_check_raw"] == "ok"

        # Semantic Drift Ratio
        drift = probes.calculate_semantic_drift_ratio()
        assert drift["status"] == "STABLE" or drift["status"] == "DRIFT_DETECTED"
        assert drift["total_cards_profiled"] == 0 # no cards with embeddings in temp test db

    def test_self_healing_ail_daemon_direct(self, test_db):
        """
        Directly asserts that SelfHealingAILDaemon executes SQLite compaction vacuuming and
        analyzes, and handles programmatic Git rollback on compile errors safely.
        """
        from solomon_self_healing_ail import SelfHealingAILDaemon
        daemon = SelfHealingAILDaemon(test_db.db_path)

        # Compaction
        res = daemon.run_database_vacuum_and_compaction()
        assert res["success"] is True

        # Rollback
        res_roll = daemon.trigger_programmatic_git_rollback("test-rebuilt-broken-service", "SyntaxError: invalid syntax")
        assert res_roll["success"] is True
        assert "git checkout main" in res_roll["revert_command_executed"]

        # Check failure card was saved in Mnemosyne
        card = test_db.get_card("SOK-FAIL-TEST_REBUILT_BROKEN_SERVICE")
        assert card is not None
        assert "SyntaxError" in card["content"]

    def test_audit_and_self_healing_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/audit/run and POST /api/mnemosyne/heal/loop
        endpoints process correct payloads, return success reports, and compile templates.
        """
        # 1. POST Audit Run
        res_audit = client.post("/api/mnemosyne/audit/run", data=json.dumps({}), content_type="application/json")
        assert res_audit.status_code == 200
        data_audit = res_audit.get_json()
        assert data_audit["status"] == "success"
        assert "semantic_memory_drift" in data_audit["self_audit_report"]

        # 2. POST Self-Heal Run
        payload_heal = {
            "candidate_name": "broken-test-mcp-service",
            "error_msg": "TimeoutExpired: Process terminated"
        }
        res_heal = client.post("/api/mnemosyne/heal/loop", data=json.dumps(payload_heal), content_type="application/json")
        assert res_heal.status_code == 200
        data_heal = res_heal.get_json()
        assert data_heal["status"] == "success"

        maint = data_heal["maintenance_report"]
        assert maint["sqlite_compaction"]["success"] is True
        assert maint["programmatic_git_rollback"]["success"] is True
        assert maint["programmatic_git_rollback"]["candidate_aborted"] == "broken-test-mcp-service"

    def test_meta_learning_engine_tuning(self):
        """
        Directly asserts that SOSS Phase 12 MetaLearningEngine dynamically tunes
        Curiosity Engine weighting coefficients based on system momentum trends.
        """
        from solomon_meta_learning import MetaLearningEngine
        weights = {
            "w_value": 1.5,
            "w_risk": 0.8
        }
        res = MetaLearningEngine.execute_meta_learning_tuning(
            current_learning_speed_ratio=1.02,
            historical_speeds=[1.01, 1.05], # Stagnating/decelerating trend
            curiosity_weights=weights
        )

        assert res["status"] == "META_LEARNING_COMPLETE"
        assert res["meta_learning_momentum"] == -0.03
        assert res["tuned_curiosity_weights"]["w_value"] == 1.70
        assert res["tuned_curiosity_weights"]["w_risk"] == 0.90
        assert len(res["structural_refactorings_triggered"]) == 2

    def test_loki_intelligence_engine_shin_and_kelly(self):
        """
        Directly asserts that Project Loki's Shin solver neutralizes overround/vig
        and Fractional Kelly staking generates correct bankroll allocations.
        """
        from solomon_loki_engine import LokiIntelligenceEngine

        # Test Shin Solver on standard binary market (implied: 52.36% / 52.36% summing to 104.72% overround)
        implied_probs = [1.0 / 1.91, 1.0 / 1.91]
        z, true_probs = LokiIntelligenceEngine.solve_shin_probabilities(implied_probs)

        assert z > 0.0
        assert abs(sum(true_probs) - 1.0) < 1e-4
        assert true_probs == [0.5, 0.5] # Shin correctly extracts true 50% fair probability!

        # Test Kelly Stake (with 55% true prob, 1.91 odds, 0.25 scaling fraction)
        stake = LokiIntelligenceEngine.calculate_kelly_stake(
            true_probability=0.55,
            decimal_odds=1.91,
            fraction=0.25
        )
        # f = fraction * (p*b - (1-p)) / b  where b = 0.91, p = 0.55
        # f = 0.25 * (0.55*0.91 - 0.45) / 0.91 = 0.25 * (0.5005 - 0.45) / 0.91 = 0.25 * 0.0505 / 0.91 = 0.01387
        assert abs(stake - 0.0139) < 1e-4

    def test_meta_learning_and_loki_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/meta-learning/tune and POST /api/command-center/loki/evaluate
        endpoints process correct payloads, calculate outputs, and return success JSON.
        """
        # 1. POST Meta-Learning
        payload_meta = {
            "current_learning_speed_ratio": 1.08,
            "historical_speeds": [1.02, 1.05],
            "curiosity_weights": {"w_value": 1.5, "w_risk": 0.8}
        }
        res_meta = client.post(
            "/api/mnemosyne/meta-learning/tune",
            data=json.dumps(payload_meta),
            content_type="application/json"
        )
        assert res_meta.status_code == 200
        data_meta = res_meta.get_json()
        assert data_meta["status"] == "success"
        assert data_meta["meta_learning_report"]["meta_learning_momentum"] == 0.03 # positive growth

        # 2. POST Loki Evaluate
        payload_loki = {
            "odds": [1.91, 1.91],
            "model_true_probability": 0.55,
            "odds_selected": 1.91,
            "kelly_fraction": 0.25
        }
        res_loki = client.post(
            "/api/command-center/loki/evaluate",
            data=json.dumps(payload_loki),
            content_type="application/json"
        )
        assert res_loki.status_code == 200
        data_loki = res_loki.get_json()
        assert data_loki["status"] == "success"

        analysis = data_loki["loki_analysis"]
        assert analysis["shin_z_informed_bettor_fraction"] > 0
        assert analysis["calculated_fractional_kelly_stake"] == 0.0139
        assert analysis["action_recommendation"] == "PLACE_BET"

    def test_distributed_node_ledger_sync(self, test_db):
        """
        Directly asserts that DistributedNodeLedger merges peer node cards delta
        back to the primary SQLite store based on confidence conflict resolution.
        """
        from solomon_distributed_ledger import DistributedNodeLedger
        ledger = DistributedNodeLedger(test_db)

        remote_cards = [
            {
                "card_id": "SOK-SYNC-NEW-CARD",
                "family": "Knowledge",
                "focus": "Synced focus",
                "content": "Synced content block from remote node.",
                "confidence": 1.0
            }
        ]

        # First sync inserts new card
        res = ledger.sync_node_ledger_deltas("macOS-Node-01", remote_cards)
        assert res["sync_summary"]["inserted_new_cards"] == 1
        assert res["sync_summary"]["updated_existing_cards"] == 0

        # Assert card was saved
        card = test_db.get_card("SOK-SYNC-NEW-CARD")
        assert card is not None
        assert "remote node" in card["content"]

        # Syncing again with same/lower confidence gets ignored
        res2 = ledger.sync_node_ledger_deltas("macOS-Node-01", remote_cards)
        assert res2["sync_summary"]["ignored_stale_cards"] == 1

        # Syncing with higher confidence triggers update
        remote_cards[0]["confidence"] = 1.8
        res3 = ledger.sync_node_ledger_deltas("macOS-Node-01", remote_cards)
        assert res3["sync_summary"]["updated_existing_cards"] == 1

    def test_wisdom_layer_vector_eval(self):
        """
        Directly asserts that SOSS WisdomLayer validates or blocks proposed system actions
        against the multi-dimensional Wisdom Vector safely.
        """
        from solomon_wisdom_layer import WisdomLayer

        # Safe operation passes
        res = WisdomLayer.evaluate_wisdom_vector(
            confidence=0.90,
            risks_rating=2.0,
            limits_within_bounds=True,
            has_human_override=False,
            is_ethically_compliant=True
        )
        assert res["decision"] == "APPROVED_FOR_EXECUTION"

        # Unethical operation is hard blocked
        res_eth = WisdomLayer.evaluate_wisdom_vector(
            confidence=0.90,
            risks_rating=2.0,
            limits_within_bounds=True,
            has_human_override=False,
            is_ethically_compliant=False
        )
        assert res_eth["decision"] == "BLOCKED"
        assert "Ethical" in res_eth["reason"]

        # High risk block, override allows bypass
        res_risk = WisdomLayer.evaluate_wisdom_vector(
            confidence=0.95,
            risks_rating=9.5, # extreme risk
            limits_within_bounds=True,
            has_human_override=False,
            is_ethically_compliant=True
        )
        assert res_risk["decision"] == "BLOCKED"

        res_risk_override = WisdomLayer.evaluate_wisdom_vector(
            confidence=0.95,
            risks_rating=9.5,
            limits_within_bounds=True,
            has_human_override=True, # bypassed
            is_ethically_compliant=True
        )
        assert res_risk_override["decision"] == "APPROVED_FOR_EXECUTION"

    def test_ledger_and_wisdom_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/ledger/sync and POST /api/mnemosyne/wisdom/evaluate
        endpoints process correct payloads, parse deltas, and output wisdom vectors.
        """
        # Clean up database state for deterministic run
        import sqlite3
        conn = sqlite3.connect("solomon_mnemosyne_demo.db")
        conn.execute("DELETE FROM knowledge_cards WHERE card_id = ?", ("SOK-LEDGER-SYNC-ROUTE-TEST",))
        conn.commit()
        conn.close()

        # 1. POST Ledger Sync
        payload_sync = {
            "node_id": "UBUNTU-LOCAL-NODE-99",
            "remote_cards": [
                {
                    "card_id": "SOK-LEDGER-SYNC-ROUTE-TEST",
                    "family": "Knowledge",
                    "focus": "Route test focus",
                    "content": "Direct test content",
                    "confidence": 1.2
                }
            ]
        }
        res_sync = client.post(
            "/api/mnemosyne/ledger/sync",
            data=json.dumps(payload_sync),
            content_type="application/json"
        )
        assert res_sync.status_code == 200
        data_sync = res_sync.get_json()
        assert data_sync["status"] == "success"
        assert data_sync["ledger_sync_report"]["sync_summary"]["inserted_new_cards"] == 1

        # 2. POST Wisdom Evaluate
        payload_wisdom = {
            "confidence": 0.45, # sub-threshold
            "risks_rating": 3.0,
            "limits_within_bounds": True,
            "has_human_override": False,
            "is_ethically_compliant": True
        }
        res_wisdom = client.post(
            "/api/mnemosyne/wisdom/evaluate",
            data=json.dumps(payload_wisdom),
            content_type="application/json"
        )
        assert res_wisdom.status_code == 200
        data_wisdom = res_wisdom.get_json()
        assert data_wisdom["status"] == "success"
        assert data_wisdom["wisdom_vector_report"]["decision"] == "BLOCKED"
        assert "override" in data_wisdom["wisdom_vector_report"]["reason"]

    def test_autonomous_tool_creation_direct(self, test_db):
        """
        Directly asserts that AutonomousToolCreator prototypes, audits, and registers
        new tools inside the Active Skill Graph and Mnemosyne DB successfully.
        """
        from solomon_skill_graph import SkillGraph
        from solomon_autonomous_tool_creator import AutonomousToolCreator

        graph = SkillGraph()
        creator = AutonomousToolCreator(test_db, graph)

        tool_id = "SKILL-SYS-CLEAN-01"
        source = "def clean_system(): return 'CLEANED'"
        res = creator.prototype_and_register_tool(tool_id, "System Cleaner", source, "clean_system()")

        assert res["status"] == "SUCCESSFULLY_REGISTERED"
        assert res["return_value"] == "CLEANED"

        # Assert card was saved directly in ACTIVE validation state
        card = test_db.get_card(f"SOK-TOOL-{tool_id.upper().replace('-', '_')}")
        assert card is not None
        assert card["validation_state"] == "ACTIVE"
        assert "CLEANED" in card["content"]

        # Assert registered inside Active Skill Graph
        assert graph.get_skill(tool_id) is not None

    def test_self_repair_engine_direct(self, test_db):
        """
        Directly asserts that SelfRepairEngine scans metrics deviations and compiles
        and compiles ACTIVE repair playbooks inside Mnemosyne DB successfully.
        """
        from solomon_self_repair import SelfRepairEngine
        repair_engine = SelfRepairEngine(test_db)

        # Trigger audit with latencies above threshold
        metrics = {
            "rolling_average_latency_ms": 15.4,
            "out_of_memory_signals": 1
        }
        res = repair_engine.audit_and_repair_system(metrics)
        assert res["faults_detected"] is True
        assert len(res["repaired_actions_executed"]) == 2
        assert res["promoted_repair_card_id"] == "SOK-REPAIR-TELEMETRY-DEVIATION"

        # Assert card was saved in ACTIVE validation state in Mnemosyne
        card = test_db.get_card("SOK-REPAIR-TELEMETRY-DEVIATION")
        assert card is not None
        assert card["validation_state"] == "ACTIVE"

    def test_tool_creation_and_self_repair_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/tools/create and POST /api/mnemosyne/self-repair/run
        endpoints process requests, execute prototyping and healing, and output success status.
        """
        # 1. POST Tools Create
        payload_tool = {
            "tool_id": "SKILL-MATH-FIB-101",
            "name": "Fibonacci Fast Solver",
            "source_code": "def fib(n=10):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n",
            "entry_call": "fib(5)"
        }
        res_tool = client.post(
            "/api/mnemosyne/tools/create",
            data=json.dumps(payload_tool),
            content_type="application/json"
        )
        assert res_tool.status_code == 200
        data_tool = res_tool.get_json()
        assert data_tool["status"] == "success"
        assert data_tool["autonomous_tool_creation_report"]["status"] == "SUCCESSFULLY_REGISTERED"
        assert data_tool["autonomous_tool_creation_report"]["return_value"] == 5

        # 2. POST Self-Repair Run
        payload_repair = {
            "rolling_average_latency_ms": 6.8,
            "out_of_memory_signals": 0
        }
        res_repair = client.post(
            "/api/mnemosyne/self-repair/run",
            data=json.dumps(payload_repair),
            content_type="application/json"
        )
        assert res_repair.status_code == 200
        data_repair = res_repair.get_json()
        assert data_repair["status"] == "success"
        assert data_repair["self_repair_audit_report"]["faults_detected"] is True
        assert data_repair["self_repair_audit_report"]["promoted_repair_card_id"] == "SOK-REPAIR-TELEMETRY-DEVIATION"

    def test_self_study_optimizer(self):
        """
        Directly asserts that the SelfStudyOptimizer tunes active vector weights
        and routing thresholds based on retrieval feedback metrics.
        """
        from solomon_self_study import SelfStudyOptimizer
        current_params = {
            "base_threshold": 0.40,
            "similarity_decay": 0.98
        }
        res = SelfStudyOptimizer.optimize_hyperparameters(
            retrieval_success_rate=0.85,
            router_accuracy_rate=0.90,
            current_params=current_params
        )

        assert res["status"] == "PARAMETERS_OPTIMIZED"
        assert res["optimized_hyperparameters"]["base_threshold"] == 0.45
        assert res["optimized_hyperparameters"]["similarity_decay"] == 0.96
        assert len(res["adjustments_made"]) == 2

    def test_study_and_research_api_routes(self, client):
        """
        Verifies POST /api/mnemosyne/study/optimize and POST /api/mnemosyne/research/evaluate
        endpoints process requests, tune RAG params, and promote research winners to SQLite.
        """
        # 1. POST Study Optimize
        payload_study = {
            "retrieval_success_rate": 0.88,
            "router_accuracy_rate": 0.91,
            "current_base_threshold": 0.50,
            "current_similarity_decay": 0.95
        }
        res_study = client.post(
            "/api/mnemosyne/study/optimize",
            data=json.dumps(payload_study),
            content_type="application/json"
        )
        assert res_study.status_code == 200
        data_study = res_study.get_json()
        assert data_study["status"] == "success"
        assert data_study["study_optimizer_report"]["status"] == "PARAMETERS_OPTIMIZED"

        # 2. POST Research Evaluate
        payload_res = {
            "project_id": "RES-NORM-999",
            "topic": "Cosine normalization performance sum",
            "candidates": [
                {
                    "name": "Normal sum method A",
                    "source_code": "def solve(): return 123",
                    "entry_call": "solve()"
                }
            ]
        }
        res_research = client.post(
            "/api/mnemosyne/research/evaluate",
            data=json.dumps(payload_res),
            content_type="application/json"
        )
        assert res_research.status_code == 200
        data_research = res_research.get_json()
        assert data_research["status"] == "success"

        report = data_research["research_project_report"]
        assert report["project_id"] == "RES-NORM-999"
        assert report["winning_candidate_name"] == "Normal sum method A"
        assert report["promoted_card_id"] == "SOK-RESEARCH-WINNER-RES_NORM_999"

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
