"""
Unit and integration tests for Solomon SOSS Phase 8: Autonomous Tool Creation & Phase 9: Self-Repair & Telemetry Probes
"""

import json
import pytest
from app import app, db, autonomous_tool_creator, self_repair_engine


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestAutonomousToolCreator:
    """
    Verifies dynamic tool prototyping, AST security scans, and Skill Factory registrations.
    """

    def test_prototype_and_audit_success(self):
        code = autonomous_tool_creator.prototype_tool("power_solver", "**")
        passed, msg = autonomous_tool_creator.perform_ast_security_audit(code)
        assert passed is True
        assert "AST Security Audit Approved" in msg

    def test_audit_failure_import_forbidden(self):
        forbidden_code = """import os\ndef test_fn(x, y):\n    return x + y"""
        passed, msg = autonomous_tool_creator.perform_ast_security_audit(forbidden_code)
        assert passed is False
        assert "forbidden from importing libraries" in msg

    def test_audit_failure_builtin_forbidden(self):
        forbidden_code = """def test_fn(x, y):\n    eval('1+1')\n    return x + y"""
        passed, msg = autonomous_tool_creator.perform_ast_security_audit(forbidden_code)
        assert passed is False
        assert "Forbidden builtin function call" in msg

    def test_build_and_register_success(self):
        success, msg, skill_data = autonomous_tool_creator.build_and_register_tool(
            tool_name="auto_subtractor",
            mathematical_operation="-",
            purpose="Dynamic math subtractor",
            inputs=["x", "y"],
            outputs=["result"]
        )
        assert success is True
        assert "successfully created" in msg
        assert skill_data["is_certified"] is True


class TestSelfRepairEngine:
    """
    Verifies background telemetry probing and self-healing DB correction triggers.
    """

    def test_telemetry_probe(self):
        telemetry = self_repair_engine.conduct_system_telemetry_probe()
        assert "api_latency_ms" in telemetry
        assert "system_ram_mb" in telemetry
        assert "database_integrity_passed" in telemetry

    def test_self_healing_low_confidence_drift(self):
        # Create a card with extremely low confidence by scaling down repeatedly
        db.upsert_card("SOK-DRIFTED-CARD", "Knowledge", "Drift test", "Content")

        # Scale down repeatedly using failure updates
        for _ in range(3):
            db.update_card_confidence("SOK-DRIFTED-CARD", "failure", 0.50)

        # Check confidence is drifted below 0.20
        card_before = db.get_card("SOK-DRIFTED-CARD")
        assert card_before["confidence"] < 0.20

        # Execute self-healing
        report = self_repair_engine.run_self_healing_routine()
        assert report["healed"] is True
        assert any("SOK-DRIFTED-CARD" in r for r in report["repairs"])

        # Check that confidence rating was restored (healed back above 0.20)
        card_after = db.get_card("SOK-DRIFTED-CARD")
        assert card_after["confidence"] > 0.15


class TestToolCreatorAndRepairAPI:
    """
    Integration tests for Flask API Tool Creator and Self-Repair endpoints.
    """

    def test_api_tool_create_workflow(self, client):
        payload = {
            "name": "api_modulo_solver",
            "mathematical_operation": "%",
            "purpose": "Finds remainder of division"
        }
        res = client.post(
            "/api/mnemosyne/tools/create",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "api_modulo_solver" in data["message"]

    def test_api_self_repair_run(self, client):
        res = client.post("/api/mnemosyne/self-repair/run")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "self_repair_report" in data
