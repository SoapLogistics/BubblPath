"""
Unified Master Testing Suite for SOSS Phases 24 to 37

Verifies context isolation, page eviction managers, P2P syncer, virtual allocation,
parameter drift watchdogs, SMT hallucination classifiers, safety guardrails,
tensor refiners, consensus ballot boxes, ternary entropy calibration, SpinQuant rotators,
QAT distillation heuristics, MSE minimization solvers, and dynamic weight sparsity pruning.
"""

import json
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestMasterPhases:
    """
    Tests SOSS Phase 24 through 37 capabilities.
    """

    def test_context_isolation_endpoint(self, client):
        payload = {
            "tenant_id": "user_Z",
            "role": "user",
            "content": "Secret transaction details"
        }
        res = client.post("/api/command-center/context/isolate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert len(data["context"]) == 1

    def test_kv_cache_eviction_endpoint(self, client):
        payload = {"page_id": "p_temp", "content": "historical logs"}
        res = client.post("/api/command-center/kv/evict", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "p_temp" in data["cached_pages"]

    def test_rag_sync_endpoint(self, client):
        import sqlite3
        conn = sqlite3.connect("solomon_mnemosyne_demo.db")
        conn.execute("DELETE FROM knowledge_cards WHERE card_id='SOK-PEER-SYNC-001'")
        conn.commit()
        conn.close()

        payload = {
            "peer_cards": [
                {
                    "card_id": "SOK-PEER-SYNC-001",
                    "family": "Knowledge",
                    "content": "Peer synchronized configuration benchmarks."
                }
            ]
        }
        res = client.post("/api/command-center/rag/sync", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["synced_cards_count"] == 1

    def test_kv_allocate_endpoint(self, client):
        payload = {"size_mb": 24.5}
        res = client.post("/api/command-center/kv/allocate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["pages_allocated"] == 7

    def test_model_drift_endpoint(self, client):
        payload = {
            "baseline": [0.1, 0.5, 0.8],
            "current": [0.1, 0.52, 0.79]
        }
        res = client.post("/api/command-center/model/drift", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["parameter_drift_ratio"] < 0.05

    def test_hallucination_classify_endpoint(self, client):
        payload = {
            "response": "Synthesize a ternary weight matrix calculation.",
            "verified_facts": ["ternary weight configurations and matrix allocations"]
        }
        res = client.post("/api/command-center/hallucination/classify", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["hallucinated"] is False

    def test_query_safety_endpoint(self, client):
        # Safe
        res_safe = client.post("/api/command-center/query/safety", json={"query": "Select all cards."})
        assert res_safe.status_code == 200
        assert res_safe.get_json()["safe"] is True

        # Unsafe
        res_unsafe = client.post("/api/command-center/query/safety", json={"query": "cat /etc/passwd"})
        assert res_unsafe.status_code == 200
        assert res_unsafe.get_json()["safe"] is False

    def test_tensor_align_endpoint(self, client):
        payload = {
            "clusters": [[0.1, 0.9], [0.3, 0.7]]
        }
        res = client.post("/api/command-center/tensor/align", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert len(data["aligned_clusters"]) == 2

    def test_consensus_ballot_endpoint(self, client):
        payload = {
            "votes": {"A": 1.5, "B": 1.2}
        }
        res = client.post("/api/command-center/consensus/ballot", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["consensus_passed"] is True

    def test_ternary_calibrate_endpoint(self, client):
        payload = {
            "weights": [0.1, -0.5, 0.9, -0.2]
        }
        res = client.post("/api/command-center/ternary/calibrate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["optimal_threshold_delta"] == 0.2975

    def test_spinquant_rotate_endpoint(self, client):
        payload = {
            "weights": [0.1, 0.4, 0.8],
            "outliers": 100
        }
        res = client.post("/api/command-center/spinquant/rotate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["spinquant_report"]["outliers_remaining"] == 5

    def test_qat_distill_endpoint(self, client):
        payload = {
            "teacher_logits": [1.0, -0.5],
            "student_logits": [0.9, -0.4]
        }
        res = client.post("/api/command-center/qat/distill", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "kl_divergence_distillation_loss" in data

    def test_activation_mse_endpoint(self, client):
        payload = {
            "original": [0.1, 0.2, 0.3],
            "quantized": [0.11, 0.19, 0.29]
        }
        res = client.post("/api/command-center/activation/mse", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["mean_squared_error"] == 0.0001

    def test_weight_prune_endpoint(self, client):
        payload = {
            "weights": [0.05, -0.8, 0.3, 0.02, 0.9],
            "sparsity": 0.40
        }
        res = client.post("/api/command-center/weight/prune", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["zeros_count"] == 2
