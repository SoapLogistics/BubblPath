"""
Unit and integration tests for Solomon SOSS Phase 4: Skill Factory
"""

import json
import pytest
from app import app, skill_factory


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSkillFactory:
    """
    Verifies Skill Package generation, compilation, safety audits, and dynamic execution.
    """

    def test_produce_and_certify_success(self):
        package = skill_factory.produce_skill(
            name="test_adder_custom",
            purpose="Adds custom values",
            inputs=["x", "y"],
            outputs=["res"],
            code="res = x + y"
        )
        assert package.is_certified is False

        success, msg = skill_factory.certify_skill("test_adder_custom")
        assert success is True
        assert package.is_certified is True

    def test_produce_and_certify_safety_violation(self):
        package = skill_factory.produce_skill(
            name="malicious_file_writer",
            purpose="Tries to open file",
            inputs=["path"],
            outputs=[],
            code="open(path, 'w').write('hack')"
        )
        success, msg = skill_factory.certify_skill("malicious_file_writer")
        assert success is False
        assert "Safety constraint violation" in msg

    def test_execute_skill_isolated_success(self):
        package = skill_factory.produce_skill(
            name="test_subtractor",
            purpose="Subtracts variables",
            inputs=["a", "b"],
            outputs=["result"],
            code="result = a - b"
        )
        skill_factory.certify_skill("test_subtractor")

        success, results, msg = skill_factory.execute_skill_isolated("test_subtractor", {"a": 20, "b": 7})
        assert success is True
        assert results["result"] == 13

    def test_execute_skill_missing_inputs(self):
        success, results, msg = skill_factory.execute_skill_isolated("test_subtractor", {"a": 20})
        assert success is False
        assert "Missing required input" in msg


class TestSkillFactoryAPI:
    """
    Integration tests for Flask API Skill Factory endpoints.
    """

    def test_api_create_and_execute_workflow(self, client):
        payload_create = {
            "name": "api_divider",
            "purpose": "Divides two variables safely",
            "inputs": ["numerator", "denominator"],
            "outputs": ["quotient"],
            "code": "quotient = numerator / denominator"
        }
        res_create = client.post(
            "/api/skills/factory/create",
            data=json.dumps(payload_create),
            content_type="application/json"
        )
        assert res_create.status_code == 200
        data_create = res_create.get_json()
        assert data_create["status"] == "success"
        assert data_create["skill"]["is_certified"] is True

        # Execute the Division skill
        payload_exec = {
            "name": "api_divider",
            "parameters": {
                "numerator": 100,
                "denominator": 5
            }
        }
        res_exec = client.post(
            "/api/skills/factory/execute",
            data=json.dumps(payload_exec),
            content_type="application/json"
        )
        assert res_exec.status_code == 200
        data_exec = res_exec.get_json()
        assert data_exec["status"] == "success"
        assert data_exec["results"]["quotient"] == 20
