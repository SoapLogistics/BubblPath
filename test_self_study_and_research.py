"""
Unit and Integration Tests for SOSS Phase 6 (Self-Study) and Phase 7 (Autonomous Research)
"""

import json
import pytest
import sqlite3
from app import app, db
from solomon_self_study_optimizer import SelfStudyOptimizer
from solomon_autonomous_research import AutonomousResearchEngine

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSelfStudyOptimizer:
    """
    Tests for self-study hyperparameter optimization.
    """

    def test_hyperparameter_tuning_low_failure_aggressive_cost(self):
        optimizer = SelfStudyOptimizer(db)
        metrics = {
            "average_latency_ms": 12.5,
            "failure_rate": 0.01,
            "total_queries": 100
        }
        res = optimizer.tune_system_hyperparameters(metrics)
        assert res["status"] == "success"
        assert res["tuning_applied"] is True
        assert res["optimized_parameters"]["routing_threshold"] == 0.10

    def test_hyperparameter_tuning_high_failure_safer_execution(self):
        optimizer = SelfStudyOptimizer(db)
        metrics = {
            "average_latency_ms": 55.0,
            "failure_rate": 0.12,
            "total_queries": 100
        }
        res = optimizer.tune_system_hyperparameters(metrics)
        assert res["status"] == "success"
        assert res["tuning_applied"] is True
        assert res["optimized_parameters"]["routing_threshold"] == 0.25
        assert res["optimized_parameters"]["reinforcement_learning_rate"] == 0.10


class TestAutonomousResearch:
    """
    Tests for independent benchmarking and research.
    """

    def test_execute_research_and_benchmark(self):
        engine = AutonomousResearchEngine(db)
        candidates = [
            {
                "name": "fast_math",
                "source_code": "def square(x):\n    return x * x",
                "test_harness": "assert square(5) == 25"
            },
            {
                "name": "slow_math",
                "source_code": "import time\ndef square(x):\n    time.sleep(0.01)\n    return x * x",
                "test_harness": "assert square(5) == 25"
            }
        ]

        res = engine.execute_independent_benchmark_research("squaring optimization", candidates)
        assert res["status"] == "success"
        assert res["winner_identified"] is True
        assert res["winner_details"]["candidate_name"] == "fast_math"
        assert res["promotion_report"]["db_persisted"] is True


class TestSelfStudyResearchAPIIntegration:
    """
    Verifies REST routes for Self-Study Tuning and Independent Research.
    """

    def test_post_self_study_tune_endpoint(self, client):
        payload = {
            "metrics": {
                "average_latency_ms": 10.0,
                "failure_rate": 0.005,
                "total_queries": 600
            }
        }
        response = client.post("/api/command-center/self-study/tune", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["tuning_applied"] is True
        assert len(data["adjustments_triggered"]) == 2

    def test_post_autonomous_research_endpoint(self, client):
        payload = {
            "research_topic": "factorial calculation",
            "candidates": [
                {
                    "name": "iterative_fact",
                    "source_code": "def fact(n):\n    f = 1\n    for i in range(1, n+1):\n        f *= i\n    return f",
                    "test_harness": "assert fact(5) == 120"
                }
            ]
        }
        response = client.post("/api/command-center/research/run", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["winner_identified"] is True
        assert data["winner_details"]["candidate_name"] == "iterative_fact"
        assert data["promotion_report"]["db_persisted"] is True
