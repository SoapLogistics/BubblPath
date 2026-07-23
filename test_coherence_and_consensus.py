"""
Unit and Integration Tests for SOSS Phase 18 (Tensor Coherence) and Phase 19 (Multi-Agent Consensus)
"""

import json
import pytest
from app import app, db
from solomon_tensor_coherence import TensorCoherenceOptimizer
from solomon_multi_agent_consensus import MultiAgentConsensus

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestTensorCoherence:
    """
    Tests for the Tensor Coherence simulated annealing.
    """

    def test_simulated_coherence_optimization(self):
        optimizer = TensorCoherenceOptimizer(db)

        initial = [0.1, 0.4, 0.8, -0.1]
        res = optimizer.run_simulated_annealing_optimization(initial_states=initial, steps=30)

        assert res["status"] == "success"
        assert res["optimal_coherence"] >= res["initial_coherence"]
        assert len(res["optimized_states"]) == 4


class TestMultiAgentConsensus:
    """
    Tests for the Collaborative Multi-Agent Consensus Protocol.
    """

    def test_weighted_consensus_rejection(self):
        consensus = MultiAgentConsensus(db)
        votes = {
            "Gabriel": True,     # Weight: 1.5
            "Mnemosyne": False,  # Weight: 1.2
            "Prometheus": False, # Weight: 1.0
            "Loki": False        # Weight: 0.8
        }
        # Approval ratio = 1.5 / 4.5 = 33% < 75% -> Rejection
        res = consensus.evaluate_action_proposal("TEST-REJECT", "risky action", votes)
        assert res["status"] == "success"
        assert res["consensus_reached"] is False
        assert res["approval_percentage"] == 33.33

    def test_weighted_consensus_approval(self):
        consensus = MultiAgentConsensus(db)
        votes = {
            "Gabriel": True,     # Weight: 1.5
            "Mnemosyne": True,   # Weight: 1.2
            "Prometheus": True,  # Weight: 1.0
            "Loki": False        # Weight: 0.8
        }
        # Approval ratio = 3.7 / 4.5 = 82% >= 75% -> Approval
        res = consensus.evaluate_action_proposal("TEST-APPROVE", "safe action", votes)
        assert res["status"] == "success"
        assert res["consensus_reached"] is True
        assert res["approval_percentage"] == 82.22


class TestCoherenceConsensusAPIIntegration:
    """
    Verifies REST routes for Tensor Coherence and Multi-Agent Consensus.
    """

    def test_post_tensor_coherence_endpoint(self, client):
        payload = {
            "initial_states": [0.0, 0.2, 0.4, 0.6],
            "steps": 10
        }
        response = client.post("/api/command-center/tensor/coherence", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "optimal_coherence" in data
        assert "optimized_states" in data

    def test_post_consensus_vote_endpoint(self, client):
        payload = {
            "proposal_id": "STABLE-ROUTING-PREF",
            "description": "Enforce local execution preferences",
            "votes": {
                "Gabriel": True,
                "Mnemosyne": True,
                "Prometheus": True,
                "Loki": True
            }
        }
        response = client.post("/api/command-center/consensus/vote", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["consensus_reached"] is True
        assert data["approval_percentage"] == 100.0
