"""
Unit and integration tests for Solomon SOSS Phase 5: Skill Graph & Dependency Maps
"""

import json
import pytest
from app import app, skill_graph


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSkillGraph:
    """
    Verifies Skill Graph topological sorting, prerequisite pathing, and cycle checks.
    """

    def test_topological_sort_linear(self):
        graph = skill_graph.__class__() # Fresh instance
        graph.add_skill("A")
        graph.add_skill("B")
        graph.add_skill("C")
        graph.add_dependency("C", "B") # C depends on B
        graph.add_dependency("B", "A") # B depends on A

        order = graph.get_topological_sort()
        # Dependency order must be prerequisite first: A -> B -> C
        assert order == ["A", "B", "C"]

    def test_cycle_detection(self):
        graph = skill_graph.__class__()
        graph.add_dependency("A", "B")
        graph.add_dependency("B", "C")
        graph.add_dependency("C", "A") # Cycle: A -> B -> C -> A

        assert len(graph.detect_cycles_dfs()) > 0

        # Topological sorting should raise an error under cycles
        with pytest.raises(ValueError) as exc:
            graph.get_topological_sort()
        assert "Circular dependency detected" in str(exc.value)

    def test_find_missing_prerequisites(self):
        graph = skill_graph.__class__()
        graph.add_dependency("active_one", "missing_one")
        graph.add_dependency("active_one", "active_two")

        active_set = {"active_one", "active_two"}
        gaps = graph.find_missing_prerequisites(active_set)
        assert gaps == {"missing_one"}

    def test_graph_analytics(self):
        graph = skill_graph.__class__()
        graph.add_dependency("B", "A")
        graph.add_dependency("C", "A") # A is a bottleneck (many depend on it)

        analytics = graph.get_graph_analytics()
        assert analytics["total_skills"] == 3
        assert analytics["total_dependencies"] == 2
        assert "A" in analytics["bottlenecks"]
        assert analytics["has_cycles"] is False


class TestSkillGraphAPI:
    """
    Integration tests for Flask API Skill Graph endpoints.
    """

    def test_api_graph_analyze(self, client):
        res = client.get("/api/skills/graph/analyze")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "topological_execution_order" in data
        assert "graph_analytics" in data
        assert "detected_missing_knowledge_gaps" in data
        assert "recommended_next_step" in data
        assert "Resolve the detected missing" in data["recommended_next_step"]
