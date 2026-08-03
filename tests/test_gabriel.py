import json
import os
import tempfile

from app import app, gabriel_loop
from gabriel_engine.core.acquisition import AcquisitionEngine
from gabriel_engine.core.assimilation_decision import AssimilationDecisionEngine
from gabriel_engine.core.behavioral_experimentation import (
    BehavioralExperimentationEngine,
)
from gabriel_engine.core.capability_extraction import CapabilityExtractionEngine
from gabriel_engine.core.crucible import Crucible
from gabriel_engine.core.dynamic_loader import DynamicCapabilityRegistry
from gabriel_engine.core.independent_construction import CleanRoomBuilder

# Import our core components
from gabriel_engine.core.models import (
    AcquisitionRecord,
    CapabilityMemoryCard,
    ProgramAnatomyCard,
)
from gabriel_engine.core.permission_gate import PermissionGate
from gabriel_engine.core.structural_comprehension import StructuralComprehensionEngine


def test_models():
    """
    Test core SOK model structure and serialization.
    """
    record = AcquisitionRecord(
        project_name="TestProject",
        source_location="test_path",
        source_type="git",
        license_detected="MIT"
    )
    d = record.to_dict()
    assert d["project_name"] == "TestProject"
    assert d["license_detected"] == "MIT"
    assert d["aggressive_mode"] is True

    anatomy = ProgramAnatomyCard(
        capability="timed leases",
        inputs=["data"],
        outputs=["status"],
        core_mechanisms=["leasing"],
        valuable_patterns=["lease_renewal"],
        solomon_relevance=["reliability"]
    )
    d_anatomy = anatomy.to_dict()
    assert d_anatomy["capability"] == "timed leases"

    cap_card = CapabilityMemoryCard(
        name="retry_on_429",
        source_project="TestProject",
        source_license="MIT",
        concept_summary="Summary"
    )
    assert cap_card.to_dict()["name"] == "retry_on_429"


def test_acquisition_and_permission_gate():
    """
    Test License Detection and Gate Lane Routing in normal and aggressive mode.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock LICENSE file
        lic_path = os.path.join(tmpdir, "LICENSE")
        with open(lic_path, "w") as f:
            f.write("This software is licensed under the Apache License 2.0")

        engine = AcquisitionEngine()

        # Test Normal Mode
        record_normal = engine.acquire(
            project_name="ApacheProject",
            source_location=tmpdir,
            aggressive_mode=False
        )
        assert record_normal.license_detected == "Apache-2.0"
        lane, justification = PermissionGate.evaluate_lane(record_normal)
        assert lane == "GREEN"

        # Test Aggressive Mode (Forces "Proprietary" to act permissively)
        record_prop = AcquisitionRecord(
            project_name="SecretSoftware",
            source_location="fake_secret_path",
            source_type="source_repository",
            license_detected="Proprietary",
            aggressive_mode=True
        )
        lane_prop, justification_prop = PermissionGate.evaluate_lane(record_prop)
        # Bypassed to study and independent recreate (Blue) but modified to optimize!
        assert lane_prop == "BLUE"
        assert "bypassed" in justification_prop.lower()


def test_structural_comprehension_and_behavioral():
    """
    Test scanning file structures, recognizing patterns, and running experiments.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write dummy python files and requirements
        with open(os.path.join(tmpdir, "app.py"), "w") as f:
            f.write("""
@app.route('/api/tasks')
def get_tasks():
    pass
""")
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("flask>=2.0.0\nrequests==2.28.1")

        scanner = StructuralComprehensionEngine()
        anatomy = scanner.scan_project(tmpdir)

        assert "Python" in anatomy.languages
        assert "flask" in anatomy.dependencies
        assert "requests" in anatomy.dependencies
        assert "/api/tasks" in anatomy.core_mechanisms or "http_api_routing" in anatomy.core_mechanisms

        # Test behavioral suite
        behav_engine = BehavioralExperimentationEngine()
        res = behav_engine.run_experiment(test_scenarios=["normal_execution", "worker_crash"])
        assert "normal_execution" in res["observations"]
        assert "worker_crash" in res["observations"]
        assert res["reliability_index"] == 1.0


def test_capability_extraction_and_decisions():
    """
    Test parsing capabilities and ratio-based score evaluations.
    """
    anatomy = ProgramAnatomyCard(
        capability="worker queue",
        inputs=["job"],
        outputs=["result"],
        core_mechanisms=["leasing"],
        valuable_patterns=["timed_lease_concurrency_control", "exponential_backoff_retry"],
        solomon_relevance=["duplicate_prevention"]
    )

    behav_results = {
        "observations": {
            "worker_crash": {"recovery_status": "Successful recovery"},
            "network_failure": {"recovery_status": "Successful recovery after 1200ms"}
        }
    }

    extractor = CapabilityExtractionEngine()
    caps = extractor.extract_capabilities(anatomy, behav_results, "OriginProj", "MIT")

    cap_names = [c.name for c in caps]
    assert "renewable_worker_lease" in cap_names
    assert "exponential_backoff_retry" in cap_names

    # Test Decision Score Calculation
    # Formula: (val * rel * comp * maint) / (leg * sec * cx * cost)
    # Standard mode (with higher legal risk)
    score_normal, action_normal, _ = AssimilationDecisionEngine.calculate_decision(
        value=5.0, reliability=4.0, compatibility=4.0, maintainability=4.0,
        legal_risk=5.0, security_risk=3.0, complexity=3.0, resource_cost=2.0,
        aggressive_mode=False
    )
    # denominator: 5 * 3 * 3 * 2 = 90
    # numerator: 5 * 4 * 4 * 4 = 320
    # score: 320 / 90 = 3.55
    assert round(score_normal, 2) == 3.56
    # 3.56 > 1.5, so it maps to "WRAP"
    assert action_normal == "WRAP"

    # Aggressive Mode (Drastically discounts legal risk and security risk to 0.1)
    score_agg, action_agg, _ = AssimilationDecisionEngine.calculate_decision(
        value=5.0, reliability=4.0, compatibility=4.0, maintainability=4.0,
        legal_risk=5.0, security_risk=3.0, complexity=3.0, resource_cost=2.0,
        aggressive_mode=True
    )
    # denominator: 0.1 * 0.1 * 3 * 2 = 0.06
    # score: 320 / 0.06 = 5333.33
    assert score_agg > 5000.0
    assert action_agg == "INTEGRATE"


def test_independent_construction():
    """
    Verify that clean-room packet compilation and executable Python code are generated.
    """
    builder = CleanRoomBuilder()
    packet, code = builder.build_native_capability(
        capability_name="renewable_worker_lease",
        concept_summary="Worker lease on SQLite"
    )

    assert "renewable_worker_lease" in packet
    assert "class RenewableWorkerLease" in code
    assert "claim_task" in code

    # Execute generated code to verify syntax and functionality!
    local_vars = {}
    exec(code, local_vars)
    RenewableWorkerLeaseClass = local_vars["RenewableWorkerLease"]

    # Run inline SQLite task lease tests on the generated clean-room module
    leaser = RenewableWorkerLeaseClass(db_path=":memory:", lease_duration_sec=2)
    leaser.add_task("task_99", "do_some_magic")

    # Claim lease
    claim = leaser.claim_task("worker_A")
    assert claim is not None
    assert claim["task_id"] == "task_99"
    assert claim["payload"] == "do_some_magic"

    # Attempt second claim before expiration (should fail)
    claim_dup = leaser.claim_task("worker_B")
    assert claim_dup is None

    # Renew lease
    assert leaser.renew_lease("task_99", "worker_A") is True

    # Complete task
    assert leaser.complete_task("task_99", "worker_A") is True


def test_crucible_and_perpetual_loop():
    """
    Verify crucible validation comparisons and the orchestrator perpetual loop.
    """
    crucible = Crucible()
    report = crucible.run_validation("exponential_backoff_retry")
    assert report.decision == "PROMOTE"
    assert report.comparison_results["latency_reduction_percent"] > 0.0

    # Test full loop
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy structure
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("# timed_lease_concurrency_control\n")

        loop_res = gabriel_loop.assimilate_project(
            project_name="MyTestProject",
            source_location=tmpdir,
            aggressive_mode=True
        )
        assert loop_res["status"] == "success"
        assert len(loop_res["capabilities_assimilated"]) > 0
        assert loop_res["loop_learning_summary"]["lane_assigned"] == "GREEN"


def test_assimilated_codex_stack():
    """
    Validates re-engineered OpenAI Codex operations running inside Gabriel.
    """
    client = app.test_client()

    # 1. Chat under Codex/Jules Orchestrator Persona
    res_chat = client.post("/chat", json={"message": "Deploy a sandbox for my branch"})
    assert res_chat.status_code == 200
    data_chat = json.loads(res_chat.data)
    assert "Jules Agentic Mode" in data_chat["reply"]

    # 2. Parallel Worktrees Endpoints
    res_wt = client.post("/api/codex/worktrees", json={
        "action": "create",
        "task_id": "codex_999",
        "origin_src_dir": "/app"
    })
    assert res_wt.status_code == 200
    data_wt = json.loads(res_wt.data)
    assert data_wt["status"] == "success"
    assert "codex_999" in data_wt["workspace_path"]

    # 3. SQLite Task board / Kanban Endpoints
    res_add = client.post("/api/codex/tasks", json={
        "action": "add",
        "task_id": "issue-442",
        "payload": "fix-flaky-test"
    })
    assert res_add.status_code == 200

    res_claim = client.post("/api/codex/tasks", json={
        "action": "claim",
        "task_id": "issue-442",
        "worker_id": "worker_beta"
    })
    assert res_claim.status_code == 200
    data_claim = json.loads(res_claim.data)
    assert data_claim["task"]["task_id"] == "issue-442"

    res_stat = client.post("/api/codex/tasks", json={
        "action": "status",
        "task_id": "issue-442"
    })
    assert json.loads(res_stat.data)["task_status"] == "active"

    # 4. Model Context Protocol Tools Endpoint
    res_mcp = client.post("/api/codex/mcp", json={
        "tool_name": "bash_exec",
        "arguments": {"command": "pytest tests/"}
    })
    assert res_mcp.status_code == 200
    data_mcp = json.loads(res_mcp.data)
    assert "pytest tests/" in data_mcp["execution_payload"]["stdout"]

    # 5. Issue-to-PR Pipeline (Jules) Endpoint
    res_pipe = client.post("/api/codex/pipeline", json={
        "issue_id": "bug-104",
        "description": "Infinite loop on bad API parameters"
    })
    assert res_pipe.status_code == 200
    data_pipe = json.loads(res_pipe.data)
    assert data_pipe["status"] == "PROMOTED_TO_PULL_REQUEST"
    assert "validation_tests_passed" in data_pipe


def test_assimilated_jules_stack():
    """
    Validates re-engineered Google Jules capabilities.
    """
    client = app.test_client()

    # 1. Dependency setup installer
    res_ins = client.post("/api/jules/install", json={
        "requirements_txt": "pytest>=8.0.0\nblack==24.1.0"
    })
    assert res_ins.status_code == 200
    payload_ins = json.loads(res_ins.data)
    assert any("pytest" in p for p in payload_ins["packages_installed"])
    assert payload_ins["compilation_status"] == "SUCCESSFUL"

    # 2. Diff Code Patcher
    res_pat = client.post("/api/jules/patch", json={
        "original_code": "def run_loop():\n    return 'error'",
        "search_pattern": "error",
        "replace_pattern": "fixed"
    })
    assert res_pat.status_code == 200
    payload_pat = json.loads(res_pat.data)
    assert payload_pat["success"] is True
    assert "fixed" in payload_pat["updated_code"]

    # 3. Recursive Test execution traceback solver
    res_loop = client.post("/api/jules/test-loop", json={
        "target_code": "def process():\n    return 'error'",
        "test_script": "assert process() == 'fixed'",
        "max_retries": 3
    })
    assert res_loop.status_code == 200
    payload_loop = json.loads(res_loop.data)
    assert payload_loop["success"] is True
    assert "fixed" in payload_loop["optimized_code"]
    assert len(payload_loop["execution_logs"]) > 0


def test_hardening_and_exception_handling():
    """
    Ensures that validation checks and LRU eviction thresholds perform correctly.
    """
    client = app.test_client()

    # 1. Parameter Type Mismatch (Expects 400 Bad Request)
    res_bad_type = client.post("/api/jules/install", json={
        "requirements_txt": 12345  # Must be string
    })
    assert res_bad_type.status_code == 400
    assert "must be a valid string" in json.loads(res_bad_type.data)["message"]

    # 2. Missing Parameters Schema check (Expects 400 Bad Request)
    res_bad_schema = client.post("/api/jules/patch", json={
        "original_code": "def run(): pass"
    })
    assert res_bad_schema.status_code == 400
    assert "must be a valid string" in json.loads(res_bad_schema.data)["message"]

    # 3. Dynamic Registry LRU cache bounds eviction check
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create unique directory cache
        registry = DynamicCapabilityRegistry(target_dir=tmpdir, max_cached_modules=1)

        # Write module 1 and 2
        registry.register_and_save("mod_one", "class ModOne:\n    def get(self): return 1")
        registry.register_and_save("mod_two", "class ModTwo:\n    def get(self): return 2")

        # Load both (which triggers eviction of mod_one!)
        registry.load_capability("mod_one")
        assert "mod_one" in registry._loaded_modules

        registry.load_capability("mod_two")
        assert "mod_two" in registry._loaded_modules
        # mod_one must be successfully evicted from the memory registry cache map
        assert "mod_one" not in registry._loaded_modules


def test_flask_endpoints():
    """
    Verify app Flask endpoints structure and responses.
    """
    client = app.test_client()

    # Get status
    res = client.get("/api/gabriel/status")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "active"
    assert "history" in data

    # Trigger assimilation with missing parameters (should return 400)
    res_bad = client.post("/api/gabriel/assimilate", json={})
    assert res_bad.status_code == 400

    # Trigger mock assimilation
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("# timed_lease_concurrency_control")

        res_ok = client.post("/api/gabriel/assimilate", json={
            "project_name": "API_Assimilation_Project",
            "source_location": tmpdir,
            "aggressive_mode": True
        })
        assert res_ok.status_code == 200
        payload = json.loads(res_ok.data)
        assert payload["status"] == "success"
        assert payload["project_name"] == "API_Assimilation_Project"

    # Get records
    res_rec = client.get("/api/gabriel/records")
    assert res_rec.status_code == 200
    records = json.loads(res_rec.data)
    assert "API_Assimilation_Project" in records

    # Get anatomies
    res_ana = client.get("/api/gabriel/anatomies")
    assert res_ana.status_code == 200
    anatomies = json.loads(res_ana.data)
    assert "API_Assimilation_Project" in anatomies

    # Get capabilities
    res_cap = client.get("/api/gabriel/capabilities")
    assert res_cap.status_code == 200
    caps = json.loads(res_cap.data)
    assert "API_Assimilation_Project" in caps

    # Get crucible reports
    res_cr = client.get("/api/gabriel/crucible")
    assert res_cr.status_code == 200

    # Get implementations
    res_impl = client.get("/api/gabriel/implementations")
    assert res_impl.status_code == 200
