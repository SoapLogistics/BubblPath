import json
import pytest
from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_study_weights_optimization(client):
    """
    1. Test SOSS Phase 6 Weight Optimization endpoint.
    """
    res = client.post("/api/mnemosyne/study/optimize", json={
        "average_latency_ms": 150.0,
        "error_rate": 0.05
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["phase"] == "SOSS Phase 6 (Self-Study Weights)"
    assert "optimized_similarity_threshold" in data


def test_sentinel_compliance_sweep(client):
    """
    2. Test SOSS Phase 17 Sentinel Sweep endpoint.
    """
    # Safe code
    res_safe = client.post("/api/command-center/sentinel/verify", json={
        "source_code": "def hello():\n    print('Hello world!')\n"
    })
    assert res_safe.status_code == 200
    data_safe = json.loads(res_safe.data)
    assert data_safe["status"] == "success"
    assert data_safe["is_safe"] is True
    assert data_safe["compliance_rating"] == "HIGH_COMPLIANCE"

    # Unsafe code containing eval
    res_unsafe = client.post("/api/command-center/sentinel/verify", json={
        "source_code": "def hello():\n    eval('print(1)')\n"
    })
    assert res_unsafe.status_code == 200
    data_unsafe = json.loads(res_unsafe.data)
    assert data_unsafe["status"] == "success"
    assert data_unsafe["is_safe"] is False
    assert "Dangerous 'eval' function call detected." in data_unsafe["issues_found"]


def test_kalshi_simulation(client):
    """
    3. Test SOSS Phase 16 Kalshi Predictor simulation.
    """
    res = client.post("/api/command-center/kalshi/simulate", json={
        "event_ticker": "KX-TEST-2026",
        "probability": 0.65,
        "yes_price_cents": 60
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["event_ticker"] == "KX-TEST-2026"
    assert data["simulation_execution_logged"] is True


def test_codex_compiler(client):
    """
    4. Test SOSS Phase 15 Codex natural language compiler.
    """
    res = client.post("/api/command-center/codex/compile", json={
        "instruction": "Compute hypotenuse of right triangle"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert "compiled_python_code" in data
    assert "auto_appended_assertions" in data


def test_synapse_blend(client):
    """
    5. Test SOSS Phase 14 Neural Synapse card merger.
    """
    # Seed source cards on SQLite
    db.upsert_card("SOK-SRC-A", "Mission", "Focus A", "Content details A")
    db.upsert_card("SOK-SRC-B", "Mission", "Focus B", "Content details B")

    res = client.post("/api/command-center/synapse/blend", json={
        "card_id_a": "SOK-SRC-A",
        "card_id_b": "SOK-SRC-B"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["blended_card_id"] == "SOK-SYNAPSE-RC-A-RC-B"


def test_quantum_tensor_coherence(client):
    """
    6. Test SOSS Phase 18 Tensor Coherence annealer.
    """
    res = client.post("/api/command-center/tensor/coherence", json={
        "initial_temperature": 5.0,
        "cooling_rate": 0.9
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["final_tensor_coherence_score"] > 0.0


def test_multi_agent_consensus(client):
    """
    7. Test SOSS Phase 19 Multi-Agent consensus voter.
    """
    res = client.post("/api/command-center/consensus/vote", json={
        "proposed_action": "Integrate 10 improvements"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["consensus_reached"] is True


def test_rag_vector_compressor(client):
    """
    8. Test SOSS Phase 21 RAG Compressor.
    """
    res = client.post("/api/command-center/vector/compress", json={
        "vector": [1.5, -2.3, 0.0, -0.4]
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["compressed_sign_vector"] == [1, 0, 1, 0]


def test_model_fusion_routing(client):
    """
    9. Test SOSS Phase 22 Fusion routing.
    """
    res = client.post("/api/command-center/model/fusion", json={
        "available_vram_mb": 6000.0
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert "allocated_weights" in data


def test_performance_prediction(client):
    """
    10. Test SOSS Phase 23 Performance prediction.
    """
    res = client.post("/api/command-center/performance/predict", json={
        "model_family": "high_precision_8B",
        "prompt_length": 1500
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert "predicted_metrics" in data
    assert data["predicted_metrics"]["estimated_vram_usage_mb"] == 4096.0
