import json
import pytest
from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_token_usage_monitor(client):
    """
    1. Test SOSS Phase 24 token usage estimation.
    """
    res = client.post("/api/command-center/tokens/monitor", json={
        "messages": [
            {"role": "user", "content": "Hello Solomon"},
            {"role": "assistant", "content": "Deploy speculation"}
        ]
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["messages_counted"] == 2
    assert data["estimated_token_usage"] > 0


def test_kv_cache_compression(client):
    """
    2. Test SOSS Phase 33 KV-Cache compression simulations.
    """
    res = client.post("/api/quantization/kv-cache/compress", json={
        "cache_size_mb": 512.0,
        "strategy": "heavy_hitter_oracle"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["original_cache_size_mb"] == 512.0
    assert data["compressed_cache_size_mb"] == 204.8


def test_speculative_decoding(client):
    """
    3. Test SOSS Phase XXXVI speculative decoding speedup predictor.
    """
    res = client.post("/api/quantization/speculative/simulate", json={
        "draft_acceptance_rate": 0.8,
        "target_step_latency_ms": 20.0,
        "draft_step_latency_ms": 4.0
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["speedup_multiplier"] > 1.0


def test_adaptive_bit_allocator(client):
    """
    4. Test SOSS Phase XXXVIII adaptive integer program layer allocator.
    """
    res = client.post("/api/quantization/bit-allocator", json={
        "layer_sensitivities": [0.95, 0.2, 0.5, 0.1],
        "target_average_bit": 4.5
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert len(data["allocations"]) == 4
    assert data["computed_average_bit_width"] == 4.0


def test_dynamic_temperature_scaler(client):
    """
    5. Test SOSS Phase XXXI generation temperature scaling.
    """
    # Seed a cognitive card
    db.upsert_card("SOK-TEMP-TEST", "Mission", "Dynamic temperature tuning", "Deterministic precision values")

    res = client.post("/api/command-center/chat/temperature", json={
        "query": "Dynamic temperature tuning",
        "base_temperature": 0.8
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["scaled_temperature"] < 0.8


def test_structured_sok_json_parser(client):
    """
    6. Test SOSS Phase XXXIX structured JSON verification.
    """
    # Valid payload
    res_val = client.post("/api/mnemosyne/cards/validate-json", json={
        "card_payload": {
            "card_id": "SOK-VALID-01",
            "family": "Mission",
            "content": "Valid content details"
        }
    })
    assert res_val.status_code == 200
    data_val = json.loads(res_val.data)
    assert data_val["status"] == "success"
    assert data_val["is_valid"] is True

    # Invalid payload
    res_inval = client.post("/api/mnemosyne/cards/validate-json", json={
        "card_payload": {
            "card_id": "SOK-INVALID-01"
        }
    })
    assert res_inval.status_code == 200
    data_inval = json.loads(res_inval.data)
    assert data_inval["status"] == "error"
    assert data_inval["is_valid"] is False


def test_hybrid_reranker(client):
    """
    7. Test SOSS Phase XXXIV hybrid semantic reranking.
    """
    res = client.post("/api/mnemosyne/search/re-rank", json={
        "query": "quantization speed",
        "candidates": [
            {"card_id": "SOK-1", "content": "Details on quantization layout and speed", "semantic_similarity": 0.6},
            {"card_id": "SOK-2", "content": "Ethics of multi-agent networks", "semantic_similarity": 0.2}
        ]
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert len(data["re_ranked_candidates"]) == 2
    assert data["re_ranked_candidates"][0]["card_id"] == "SOK-1"


def test_automated_pr_creator(client):
    """
    8. Test SOSS Phase XXXV sandbox pull request builder.
    """
    res = client.post("/api/jules/pull-request", json={
        "branch_name": "jules-patch-99",
        "title": "Optimize spec dec",
        "description": "Throughput upgrades"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["pr_id"] == 101
    assert data["state"] == "OPEN"


def test_sok_card_integrity_auditor(client):
    """
    9. Test SOSS Phase XXXVII SOK schema integrity audit.
    """
    # Create a malformed card lacking focus
    db.upsert_card("SOK-MALFORMED", "Mission", "", "Brief")

    res = client.get("/api/mnemosyne/cards/integrity-audit")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["total_cards_scanned"] > 0
    # MALFORMED card should be caught by integrity scans
    assert data["malformed_cards_found"] > 0


def test_self_study_learning_rate(client):
    """
    10. Test SOSS Phase XXX learning rate speed optimization.
    """
    res = client.post("/api/mnemosyne/study/learning-rate", json={
        "consecutive_successes": 8,
        "base_learning_rate": 0.08
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["optimized_learning_rate"] < 0.08
