import os
import json
import tempfile
import pytest
from solomon_knowledge_cards import MnemosyneRuntime
from solomon_knowledge_cards.runtime import get_dynamic_context_budget
from solomon_knowledge_cards.embeddings import SemanticEmbedder, RAGVectorCompressor
from solomon_knowledge_cards.graph_engine import KnowledgeGraph, SelfStudyOptimizer, PrometheusCuriosityEngine
from solomon_knowledge_cards.loki_engine import LokiEngine, KalshiPredictor
from solomon_knowledge_cards.resource_monitor import DynamicContextBudgeter, get_scaled_memory_cap
from solomon_knowledge_cards.advanced_optimizers import (
    SystemSentinel, TensorCoherenceOptimizer, MultiAgentConsensus,
    MultiModelFusionRouter, PerformancePredictor
)

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

    import app as app_module
    app_module.runtime = MnemosyneRuntime(db_path=temp_db)
    app_module.ACTIONS_API_KEY = "TEST_ACTIONS_API_KEY"
    app_module.loki_engine = LokiEngine(app_module.runtime)

    with app_module.app.test_client() as client:
        yield client


# --- 1. Dynamic Context & Advanced Embeddings Tests ---

def test_dynamic_context_budgets():
    """Verify that dynamic context budgets adjust based on active model targets."""
    # Test gpt-4o
    os.environ["SOLOMON_MODEL"] = "gpt-4o"
    assert get_dynamic_context_budget() == 64000

    # Test gpt-3.5
    os.environ["SOLOMON_MODEL"] = "gpt-3.5-turbo"
    assert get_dynamic_context_budget() == 16000

    # Test llama/local
    os.environ["SOLOMON_MODEL"] = "local-llama-3"
    assert get_dynamic_context_budget() == 12000

    if "SOLOMON_MODEL" in os.environ:
        del os.environ["SOLOMON_MODEL"]


def test_concept_projector_embeddings():
    """Verify that the Concept Projection vectorizer produces semantic alignments and matches expectations."""
    embedder = SemanticEmbedder()

    sports_text = "Highly predictive sports odds betting arbitrage."
    db_text = "SQLite database table schema migration query."

    v_sports = embedder.get_embedding(sports_text)
    v_db = embedder.get_embedding(db_text)

    assert len(v_sports) == 128
    assert len(v_db) == 128

    sim = embedder.cosine_similarity(v_sports, v_db)
    assert sim < 0.40
    assert abs(embedder.cosine_similarity(v_sports, v_sports) - 1.0) < 1e-6


# --- 2. Knowledge Graph & Topological Sort Tests ---

def test_knowledge_graph_topological_sort(runtime_test):
    """Verify that Kahn's algorithm resolves prerequisites topologically (dependencies first)."""
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES
            ('KC-A', 'PROCEDURE', 'Card A', 'Prerequisite', 'Do A first.', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-B', 'PROCEDURE', 'Card B', 'Mid step', 'Do B second.', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-C', 'PROCEDURE', 'Card C', 'Final step', 'Do C last.', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now')
        """)

    runtime_test.add_card_link("KC-B", "KC-A", "DEPENDS_ON")
    runtime_test.add_card_link("KC-C", "KC-B", "DEPENDS_ON")

    graph = KnowledgeGraph(runtime_test)
    topo = graph.resolve_topology()

    idx_a = topo.index("KC-A")
    idx_b = topo.index("KC-B")
    idx_c = topo.index("KC-C")

    assert idx_a < idx_b
    assert idx_b < idx_c


# --- 3. Pre-emptive Safeguards & Auto-Financing Tests ---

def test_preemptive_safeguards_injection(runtime_test):
    """Verify that semantically linked FAILURE or REPAIR cards are successfully retrieved as safeguards."""
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES
            ('KC-PROC-SQL', 'PROCEDURE', 'SQL execute flow', 'Database procedure', 'Query execution details.', 'APPROVED', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-FAIL-SQL', 'FAILURE', 'SQL injection risk', 'Database failure', 'Vulnerable to dynamic string injections. Fix: use parameters.', 'APPROVED', 'PUBLIC', '[]', 'now', 'now')
        """)

    runtime_test.add_card_link("KC-FAIL-SQL", "KC-PROC-SQL", "DEPENDS_ON")

    graph = KnowledgeGraph(runtime_test)
    safeguards = graph.get_failure_safeguards_for_query(query="execute flow", clearance="PUBLIC")

    assert len(safeguards) == 1
    assert safeguards[0]["card_id"] == "KC-FAIL-SQL"
    assert "use parameters" in safeguards[0]["body"]


def test_auto_financing_ram_cap_scaling(runtime_test):
    """Verify that memory cap dynamically scales up in proportion to Loki's net betting profit."""
    assert get_scaled_memory_cap() == 1536.0

    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO loki_bets (bet_id, sport, fixture, market, outcome, odds, shin_prob, kelly_fraction, stake, status, profit_loss, created_at)
            VALUES
            ('bet-win-1', 'Premier League', 'Manchester Utd vs Chelsea', 'Moneyline', 'Draw', 3.20, 0.35, 0.05, 100.0, 'WON', 220.0, 'now'),
            ('bet-win-2', 'NBA', 'Lakers vs Celtics', 'Moneyline', 'Lakers Win', 1.90, 0.55, 0.08, 200.0, 'WON', 180.0, 'now')
        """)

    os.environ["SOLOMON_DB_PATH"] = runtime_test.db_path

    scaled_cap = get_scaled_memory_cap()
    assert scaled_cap == 1936.0

    with conn:
        conn.execute("""
            INSERT INTO loki_bets (bet_id, sport, fixture, market, outcome, odds, shin_prob, kelly_fraction, stake, status, profit_loss, created_at)
            VALUES ('bet-jackpot', 'NFL', 'Super Bowl', 'Moneyline', 'Chiefs', 5.0, 0.50, 0.10, 1000.0, 'WON', 4000.0, 'now')
        """)

    assert get_scaled_memory_cap() == 3072.0

    if "SOLOMON_DB_PATH" in os.environ:
        del os.environ["SOLOMON_DB_PATH"]


# --- 4. SOSS 10 Advanced Phases Unit Tests ---

def test_loki_dynamic_risk_profiles(runtime_test):
    """Verify that Loki's risk profile parameter can be calibrated dynamically."""
    loki = LokiEngine(runtime_test)
    assert loki.risk_profile == "QUARTER_KELLY"
    assert loki.get_risk_fraction() == 0.25

    assert loki.set_risk_profile("half_kelly") is True
    assert loki.risk_profile == "HALF_KELLY"
    assert loki.get_risk_fraction() == 0.50

    assert loki.set_risk_profile("full_kelly") is True
    assert loki.risk_profile == "FULL_KELLY"
    assert loki.get_risk_fraction() == 1.00

    assert loki.set_risk_profile("invalid_profile") is False


def test_kalshi_prediction_market_ev():
    """Verify that KalshiPredictor computes contract expected value (EV) and stake correctly."""
    predictor = KalshiPredictor(None)
    picks = predictor.calculate_contract_value_picks()
    assert len(picks) > 0
    first_pick = picks[0]
    assert "ticker" in first_pick
    assert first_pick["expected_value"] > 1.02
    assert first_pick["kelly_fraction"] > 0.0


def test_system_sentinel_syntax_scanner():
    """Verify that SystemSentinel parses python syntax correctly."""
    sentinel = SystemSentinel()
    report = sentinel.scan_workspace_syntax()
    assert report["health_score"] == 100.0
    assert report["total_scanned_files"] > 0
    assert report["failed_files_count"] == 0


def test_tensor_coherence_simulated_annealing():
    """Verify simulated annealing increases conceptual coherence configurations."""
    optimizer = TensorCoherenceOptimizer(initial_coherence=0.45)
    result = optimizer.optimize_coherence()
    assert result["steps_taken"] > 0
    assert result["best_coherence"] >= 0.45


def test_multi_agent_consensus_voting():
    """Verify multi-agent worker weighted voting satisfies the >75% approval threshold."""
    consensus = MultiAgentConsensus()

    # Yes votes from all agents -> consensus achieved
    votes_all = {"gabriel": True, "mnemosyne": True, "prometheus": True, "loki": True}
    res_all = consensus.evaluate_consensus("DELETE_DATABASE", votes_all)
    assert res_all["consensus_achieved"] is True
    assert res_all["approval_margin"] == 1.0

    # No votes from Gabriel (weight 0.35) -> yes weight is 0.65 -> consensus rejected (<= 0.75)
    votes_partial = {"gabriel": False, "mnemosyne": True, "prometheus": True, "loki": True}
    res_partial = consensus.evaluate_consensus("DELETE_DATABASE", votes_partial)
    assert res_partial["consensus_achieved"] is False
    assert res_partial["approval_margin"] == 0.65


def test_dynamic_context_budgeter():
    """Verify context size budget scales dynamically under memory cap pressure."""
    budgeter = DynamicContextBudgeter(base_budget_chars=16000)
    result = budgeter.calculate_sliding_context_budget()
    assert "allocated_context_budget_chars" in result
    assert result["allocated_context_budget_chars"] <= 16000


def test_rag_vector_compressor_1bit():
    """Verify 1-bit sign quantization and index savings estimations."""
    compressor = RAGVectorCompressor()
    vector = [0.15, -0.22, 0.88, -0.01, 0.00]
    compressed = compressor.compress_vector_to_1bit(vector)

    # 1 if component >= 0 else -1
    assert compressed == [1, -1, 1, -1, 1]

    savings = compressor.estimate_compression_savings(100, len(vector))
    assert savings["vectors_index_count"] == 100
    assert savings["footprint_reduction_ratio"] > 0.0


def test_multi_model_fusion_routing():
    """Verify that multi-model fusion router selects optimal lanes based on latency SLAs."""
    router = MultiModelFusionRouter()

    # Low latency SLA (0.2s) must select high throughput lane (COMPRESSED_INT4)
    constraints_low = {"sla_max_latency_sec": 0.2, "vram_available_gb": 8.0}
    res_low = router.select_optimal_model_lane(constraints_low)
    assert res_low["selected_optimal_lane"] == "COMPRESSED_INT4"

    # Spacious SLA & RAM -> FP16 lane is APPROVED
    constraints_high = {"sla_max_latency_sec": 40.0, "vram_available_gb": 16.0}
    res_high = router.select_optimal_model_lane(constraints_high)
    fp16_eval = [lane for lane in res_high["lanes_evaluation"] if lane["lane_name"] == "HIGH_PRECISION_FP16"][0]
    assert fp16_eval["status"] == "APPROVED"


def test_performance_footprint_predictor():
    """Verify that latent performance projects scale mathematically correctly."""
    predictor = PerformancePredictor()
    res = predictor.predict_performance_footprint(2048)
    assert res["predicted_latency_seconds"] > 0.0
    assert res["predicted_vram_required_gb"] > 1.2
    assert res["predicted_process_rss_ram_mb"] > 250.0


def test_self_study_weight_tuner(runtime_test):
    """Verify retrieval weight tuning based on down-stream success rate logs."""
    tuner = SelfStudyOptimizer(runtime_test)
    assert tuner.retrieval_threshold == 0.50

    # High success rate should lower threshold (broader recall)
    res_high = tuner.optimize_retrieval_thresholds(0.95)
    assert res_high["new_threshold"] < 0.50

    # Low success rate should narrow thresholds
    tuner.retrieval_threshold = 0.50
    res_low = tuner.optimize_retrieval_thresholds(0.40)
    assert res_low["new_threshold"] > 0.50


def test_prometheus_curiosity_gap_scanner(runtime_test):
    """Verify Prometheus curiosity engine discovers isolated knowledge cards."""
    engine = PrometheusCuriosityEngine(runtime_test)

    # Initially we have no cards -> no isolated cards
    assert len(engine.scan_for_knowledge_gaps()) == 0

    # Insert an isolated card (no link references)
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES ('KC-ISOLATED', 'KNOWLEDGE', 'Isolated node', 'isolated', 'isolated content', 'APPROVED', 'PUBLIC', '[]', 'now', 'now')
        """)

    gaps = engine.scan_for_knowledge_gaps()
    assert len(gaps) == 1
    assert gaps[0]["target_card_id"] == "KC-ISOLATED"


# --- 5. Flask Endpoints Verification Tests ---

def test_advanced_endpoints_auth(flask_client):
    """Verify that all 10 advanced command center routes enforce Bearer token signatures."""
    endpoints = [
        ("/api/command-center/loki/calibrate", "POST", {"risk_profile": "HALF_KELLY"}),
        ("/api/command-center/kalshi/simulate", "POST", {}),
        ("/api/command-center/sentinel/verify", "POST", {}),
        ("/api/command-center/tensor/coherence", "POST", {"initial_coherence": 0.55}),
        ("/api/command-center/consensus/vote", "POST", {"action": "TEST", "votes": {}}),
        ("/api/command-center/context/budget", "POST", {}),
        ("/api/command-center/vector/compress", "POST", {"vector": [0.1, -0.2]}),
        ("/api/command-center/model/fusion", "POST", {"constraints": {}}),
        ("/api/command-center/performance/predict", "POST", {"sequence_length": 1024}),
        ("/api/mnemosyne/study/optimize", "POST", {"success_rate": 0.85})
    ]

    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    for path, method, payload in endpoints:
        # Check without auth -> 401
        resp_no_auth = flask_client.post(path, json=payload)
        assert resp_no_auth.status_code == 401

        # Check with correct auth -> 200
        resp_with_auth = flask_client.post(path, headers=headers, json=payload)
        assert resp_with_auth.status_code == 200
        assert resp_with_auth.json["ok"] is True
