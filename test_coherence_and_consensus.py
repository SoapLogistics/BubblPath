"""
Unit and Integration Tests for SOSS Phase 18 and Phase 19 (Tensor Coherence & Multi-Agent Consensus)
"""

import json
import pytest
from app import app
from solomon_tensor_coherence import TensorCoherenceOptimizer
from solomon_multi_agent_consensus import MultiAgentConsensus

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_tensor_coherence_simulated_annealing():
    scores = [0.9, 0.4, 0.85, 0.35]
    res = TensorCoherenceOptimizer.optimize_coherence(scores, temperature=10.0, steps=5)
    assert res["optimized_scores_sum"] >= res["initial_scores_sum"]

def test_tensor_coherence_endpoint(client):
    payload = {"initial_scores": [0.75, 0.5, 0.95]}
    resp = client.post("/api/command-center/tensor/coherence", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert "tensor_coherence_result" in data

def test_multi_agent_consensus_voting():
    # Test approved proposal (low risk score)
    res_approve = MultiAgentConsensus.cast_consensus_votes("Deploy ast patch to server.", risk_score=0.3)
    assert res_approve["determination"] == "APPROVED"
    assert res_approve["authorized"] is True

    # Test rejected proposal (extreme risk score)
    res_reject = MultiAgentConsensus.cast_consensus_votes("Re-write root database structures in flight.", risk_score=0.95)
    assert res_reject["determination"] == "REJECTED"
    assert res_reject["authorized"] is False

def test_multi_agent_consensus_endpoint(client):
    payload = {"action_proposal": "Inject optimization logic", "risk_score": 0.4}
    resp = client.post("/api/command-center/consensus/vote", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"
    assert "consensus_vote_result" in data
