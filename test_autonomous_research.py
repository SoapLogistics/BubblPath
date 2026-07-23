"""
Unit and integration tests for Solomon SOSS Phase 7: Autonomous Research & Proactive Evaluation
"""

import json
import pytest
from app import app, autonomous_researcher
from solomon_autonomous_research import ResearchCandidate


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestAutonomousResearch:
    """
    Verifies comparative evaluations, candidate scoring, and API integrations.
    """

    def test_comparative_research_winner_selection(self):
        researcher = autonomous_researcher.__class__()
        cand1 = ResearchCandidate("solver_linear", "code", expected_latency_ms=10.0, accuracy=0.98) # utility = 100*0.98 - 0.5*10 = 98 - 5 = 93
        cand2 = ResearchCandidate("solver_greedy", "code", expected_latency_ms=1.0, accuracy=0.95)   # utility = 100*0.95 - 0.5*1 = 95 - 0.5 = 94.5 (winner)

        report = researcher.conduct_comparative_research("matrix_solving_benchmark", [cand1, cand2])
        assert report["winner"]["name"] == "solver_greedy"
        assert len(report["archived_losers"]) == 1
        assert report["archived_losers"][0]["name"] == "solver_linear"


class TestAutonomousResearchAPI:
    """
    Integration tests for Flask API research endpoints.
    """

    def test_api_research_evaluate_workflow(self, client):
        payload = {
            "project_name": "picks_consensus_model",
            "candidates": [
                {"name": "cons_pow_bias", "latency_ms": 15.0, "accuracy": 0.94},
                {"name": "cons_factor_weight", "latency_ms": 4.0, "accuracy": 0.91}
            ]
        }
        res = client.post(
            "/api/mnemosyne/research/evaluate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = res.get_json()
        assert "winner" in data
        assert "archived_losers" in data
        assert "PROMOTE" in data["decision"]
