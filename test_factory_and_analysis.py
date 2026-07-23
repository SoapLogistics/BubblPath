"""
Unit and Integration Tests for SOSS Phase 4 (Skill Factory) and Phase 5 (Skill Graph & Dependency Maps)
"""

import json
import pytest
from app import app, db
from solomon_skill_factory import SkillPackage, SkillFactory
from solomon_skill_graph import SkillGraph

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSkillFactory:
    """
    Tests for modular Skill Package synthesis and validation.
    """

    def test_skill_package_compilation_and_validation(self):
        factory = SkillFactory(db)
        package = SkillPackage(
            name="jules-fibonacci-calculator",
            purpose="Calculate Nth Fibonacci number safely",
            inputs={"n": "int"},
            outputs="int",
            source_code="def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)",
            unit_tests="assert fib(6) == 8"
        )

        res = factory.validate_and_register_skill(package)
        assert res["status"] == "success"
        assert res["unit_test_passed"] is True
        assert res["db_registered"] is True
        assert res["card_id"] == "SOK-SKILL-JULES_FIBONACCI_CALCULATOR"

        # Verify card contents in database
        card = db.get_card("SOK-SKILL-JULES_FIBONACCI_CALCULATOR")
        assert card["status"] == "ACTIVE"
        assert "Calculate Nth Fibonacci number safely" in card["content"]


class TestSkillGraphAnalysis:
    """
    Tests for Phase 5 Graph Prerequisite, Missing Vector, and Redundancy diagnostics.
    """

    def test_transitive_redundancies_and_recommendations(self):
        graph = SkillGraph()

        # Scenario:
        # C depends on B and A
        # B depends on A
        # The link A -> C is transitively redundant since C -> B -> A exists.
        graph.register_skill("A", "Base component")
        graph.register_skill("B", "Intermediate engine", ["A"])
        graph.register_skill("C", "Full capability pipeline", ["B", "A"])

        analysis = graph.analyze_graph_structures()
        assert len(analysis["structural_redundancies"]) == 1
        redundant = analysis["structural_redundancies"][0]
        assert redundant["node"] == "C"
        assert redundant["redundant_dependency"] == "A"

        recommendation = graph.generate_learning_recommendation()
        assert recommendation["status"] == "success"
        assert recommendation["recommended_next_skill"] == "A"
        assert recommendation["detected_redundancies_count"] == 1


class TestSkillsFactoryAnalysisAPIIntegration:
    """
    Verifies REST routing interfaces for Skill creation and Graph diagnosis.
    """

    def test_post_skills_factory_create_endpoint(self, client):
        payload = {
            "name": "jules-prime-checker",
            "purpose": "Verify if number is prime",
            "inputs": {"n": "int"},
            "outputs": "bool",
            "source_code": "def is_prime(n):\n    if n <= 1: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True",
            "unit_tests": "assert is_prime(7) is True\nassert is_prime(10) is False"
        }
        response = client.post("/api/command-center/skills/factory/create", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["unit_test_passed"] is True
        assert data["db_registered"] is True
        assert data["card_id"] == "SOK-SKILL-JULES_PRIME_CHECKER"

    def test_get_skills_graph_analyze_endpoint(self, client):
        response = client.get("/api/command-center/skills/graph/analyze")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        # Verify graph analysis payload contains diagnostics and recommendations
        assert "graph_diagnostics" in data
        assert "recommendation" in data
        assert "detected_redundancies_count" in data["recommendation"]
