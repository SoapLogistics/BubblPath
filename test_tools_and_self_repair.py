"""
Unit and Integration Tests for SOSS Phase 8 (Autonomous Tool Creation) and Phase 9 (Self-Repair)
"""

import json
import pytest
from app import app, db
from solomon_autonomous_tool_creator import AutonomousToolCreator
from solomon_self_repair import SelfAuditProbes, SelfRepairEngine

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestAutonomousToolCreator:
    """
    Tests for automated tool synthesis and safety audits.
    """

    def test_tool_safety_block_os_import(self):
        creator = AutonomousToolCreator(db)
        # Import os is blocked
        source = "import os\ndef test(): pass"
        safe, msg = creator.audit_tool_safety(source)
        assert safe is False
        assert "Blocked import 'os'" in msg

    def test_tool_safety_block_eval_call(self):
        creator = AutonomousToolCreator(db)
        # Call eval is blocked
        source = "def test():\n    eval('2+2')"
        safe, msg = creator.audit_tool_safety(source)
        assert safe is False
        assert "Dangerous builtin call 'eval'" in msg

    def test_tool_safety_pass_and_register(self):
        creator = AutonomousToolCreator(db)
        source = "def add(x, y):\n    return x + y"
        tests = "assert add(2, 3) == 5"

        res = creator.prototype_and_register_tool(
            tool_name="jules-addition-tool",
            purpose="Add two values",
            inputs={"x": "int", "y": "int"},
            outputs="int",
            source_code=source,
            unit_tests=tests
        )
        assert res["status"] == "success"
        assert res["verified"] is True
        assert res["db_registered"] is True
        assert res["card_id"] == "SOK-TOOL-JULES_ADDITION_TOOL"


class TestSelfRepair:
    """
    Tests for self-audit probes and automated self-repair templates.
    """

    def test_self_repair_flow_ram_pressure(self):
        probes = SelfAuditProbes(db)
        engine = SelfRepairEngine(db)

        # Trigger RAM pressure probe finding
        findings = probes.perform_system_self_audit(current_rss_mb=1600.0, route_latency_ms=25.0)
        assert len(findings) == 1
        assert findings[0]["probe_name"] == "ram_pressure"

        # Execute self repair
        report = engine.execute_self_repair_loops(findings)
        assert report["status"] == "success"
        assert report["repairs_count"] == 1
        assert report["repairs_log"][0]["action_taken"] == "gc_collect_and_cache_flush"
        assert report["overall_status"] == "RECONCILED"


class TestToolsSelfRepairAPIIntegration:
    """
    Verifies REST routes for tool creation and self-repair loops.
    """

    def test_post_tools_create_endpoint_success(self, client):
        payload = {
            "tool_name": "jules-subtraction-tool",
            "purpose": "Subtract values",
            "inputs": {"x": "int", "y": "int"},
            "outputs": "int",
            "source_code": "def sub(x, y):\n    return x - y",
            "unit_tests": "assert sub(10, 3) == 7"
        }
        response = client.post("/api/command-center/tools/create", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["verified"] is True
        assert data["db_registered"] is True
        assert data["card_id"] == "SOK-TOOL-JULES_SUBTRACTION_TOOL"

    def test_post_self_repair_run_endpoint_reconciled(self, client):
        payload = {
            "current_rss_mb": 1580.0,
            "route_latency_ms": 120.0
        }
        response = client.post("/api/command-center/self-repair/run", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["repairs_count"] == 2
        assert data["overall_status"] == "RECONCILED"
