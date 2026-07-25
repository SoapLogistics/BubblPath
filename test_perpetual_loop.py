"""
Unit and Integration Tests for Solomon Perpetual Learning Loop and Active Skill Graph.
"""

import json
import pytest
from app import app
from solomon_skill_graph import SkillGraph, SandboxExecutor

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSkillGraph:
    """
    Tests topological sequence resolution and cycle checks.
    """

    def test_topological_sort_success(self):
        graph = SkillGraph()
        graph.register_skill("A", "Analyze")
        graph.register_skill("B", "Build", ["A"])
        graph.register_skill("C", "Compile", ["B", "A"])

        sequence = graph.resolve_execution_order()
        assert len(sequence) == 3
        # A has no dependencies, B depends on A, C depends on B
        assert sequence.index("A") < sequence.index("B")
        assert sequence.index("B") < sequence.index("C")

    def test_circular_dependency_error(self):
        graph = SkillGraph()
        graph.register_skill("X", "First", ["Y"])
        graph.register_skill("Y", "Second", ["X"])

        with pytest.raises(ValueError, match="Circular dependency detected"):
            graph.resolve_execution_order()


class TestSandboxExecutor:
    """
    Tests subprocess quarantine, execution limits, and timeouts.
    """

    def test_sandbox_success(self):
        source = "print('hello from sandbox')"
        res = SandboxExecutor.execute_quarantined_code(source)
        assert res["success"] is True
        assert res["status"] == "COMPLETED_SUCCESS"
        assert res["stdout"].strip() == "hello from sandbox"

    def test_sandbox_syntax_error(self):
        source = "print('unclosed quote"
        res = SandboxExecutor.execute_quarantined_code(source)
        assert res["success"] is False
        assert res["status"] == "COMPLETED_ERROR"
        assert "SyntaxError" in res["stderr"]

    def test_sandbox_timeout_interception(self):
        # Trigger an infinite sleep that exceeds 1.0s safety limit
        source = "import time\ntime.sleep(10)"
        res = SandboxExecutor.execute_quarantined_code(source, timeout_sec=1.0)
        assert res["success"] is False
        assert res["status"] == "QUARANTINED_TIMEOUT"
        assert "terminated" in res["message"]


class TestPerpetualLoopAPIIntegration:
    """
    Verifies SOSS Skill Graph and 7-Stage Perpetual Loop REST API execution.
    """

    def test_get_skills_sequence(self, client):
        response = client.get("/api/mnemosyne/skills")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "jules_dependency_installer" in data["skills_registered"]
        assert data["topological_execution_sequence"].index("jules_code_patcher") < data["topological_execution_sequence"].index("jules_test_runner_loop")

    def test_execute_sandboxed_skill_endpoint(self, client):
        payload = {
            "source_code": "import math\nprint(math.sqrt(16.0))"
        }
        response = client.post("/api/mnemosyne/skills/execute", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["execution_result"]["success"] is True
        assert data["execution_result"]["stdout"].strip() == "4.0"

    def test_execute_cognitive_perpetual_loop_endpoint(self, client):
        payload = {
            "simulated_memory_mb": 1405.0,
            "test_script": "print('Dynamic sandbox test success')"
        }
        response = client.post("/api/mnemosyne/perpetual-loop", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        # Verify 7-Stage metrics
        assert "cycle_duration_ms" in data["cycle_metadata"]
        stages = data["stages"]
        assert stages["observe"]["status"] == "NORMAL"
        assert stages["understand"]["system_stabilization_status"] == "OPTIMAL"
        assert stages["build"]["ampba_feasible"] is True
        assert stages["test"]["sandbox_status"] == "COMPLETED_SUCCESS"
        assert stages["test"]["stdout"] == "Dynamic sandbox test success"
        assert stages["remember"]["promotion_success"] is True
        assert stages["teach_itself"]["outcome_registered"] == "success"
        assert len(stages["repeat_forever"]["topologically_resolved_skills_sequence"]) > 0
