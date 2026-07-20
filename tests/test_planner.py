import os
import datetime
import json
import pytest

# Configure a unique test DB path at module level BEFORE importing app
os.environ["SOLOMON_DB_PATH"] = "test_planner_only.db"
os.environ["SOLOMON_ACTIONS_API_KEY"] = "secure_test_key"

from app import app, db_manager, repository
from solomon_knowledge_cards.models.card import KnowledgeCard

@pytest.fixture
def planner_client():
    app.config["TESTING"] = True
    # Clean database before run
    if os.path.exists("test_planner_only.db"):
        os.remove("test_planner_only.db")
    db_manager._init_db()

    with app.test_client() as client:
        yield client, repository

    if os.path.exists("test_planner_only.db"):
        os.remove("test_planner_only.db")

def test_planner_safeguard_and_arbitration(planner_client):
    client, repo = planner_client
    now_str = datetime.datetime.now(datetime.UTC).isoformat()
    headers = {"Authorization": "Bearer secure_test_key"}

    # -------------------------------------------------------------
    # 1. Test baseline planning without memory context
    # -------------------------------------------------------------
    response = client.post("/api/command-center/planner/draft", json={
        "task_id": "T-PLAN-01",
        "objective": "Deploy openhands container to port 3000"
    }, headers=headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    plan = data["plan"]
    assert plan["task_id"] == "T-PLAN-01"
    assert len(plan["injected_safeguards"]) == 0
    assert len(plan["steps"]) == 3
    assert plan["steps"][0]["action"] == "Check port availability and system resources."

    # -------------------------------------------------------------
    # 2. Add FAILURE and REPAIR memories to database
    # -------------------------------------------------------------
    fail_card = KnowledgeCard(
        card_id="FC-PORT-CONFLICT", card_type="FAILURE", schema_version="1.0.0", title="OpenHands port 3000 busy failure", summary="S", body="Port 3000 is occupied.",
        status="ACTIVE", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=["port"],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repair_card = KnowledgeCard(
        card_id="RC-PORT-REWRITE", card_type="REPAIR", schema_version="1.0.0", title="Remediation for port 3000 busy conflict", summary="Rewrite port to 3001 pre-emptively", body="Rewrite port 3000 to 3001 pre-emptively to resolve binding conflicts.",
        status="ACTIVE", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=["port"],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repo.create_card(fail_card)
    repo.create_card(repair_card)

    # -------------------------------------------------------------
    # 3. Test planning WITH memory context (pre-emptive safeguard injection)
    # -------------------------------------------------------------
    response_with_memory = client.post("/api/command-center/planner/draft", json={
        "task_id": "T-PLAN-02",
        "objective": "Deploy openhands container to port 3000"
    }, headers=headers)
    assert response_with_memory.status_code == 201
    data_wm = json.loads(response_with_memory.data)
    plan_wm = data_wm["plan"]

    # Verify that pre-emptive safeguard was injected
    assert len(plan_wm["injected_safeguards"]) == 1
    assert plan_wm["injected_safeguards"][0]["triggered_by_repair"] == "RC-PORT-REWRITE"
    assert len(plan_wm["steps"]) == 4
    assert "PRE-EMPTIVE SAFEGUARD" in plan_wm["steps"][0]["action"]

    # -------------------------------------------------------------
    # 4. Test plan execution and Tool Configuration Arbitration
    # -------------------------------------------------------------
    exec_response = client.post("/api/command-center/planner/execute", json={
        "plan_id": plan_wm["plan_id"],
        "port": 3000
    }, headers=headers)
    assert exec_response.status_code == 200
    exec_data = json.loads(exec_response.data)
    assert exec_data["plan_status"] == "EXECUTED"

    # Check that execution config was pre-emptively arbitrated and rewritten from 3000 to 3001!
    hist = exec_data["execution_history"]
    safeguard_step = [h for h in hist if h["step_number"] == 1][0]
    assert safeguard_step["config_applied"]["port"] == 3001
    assert "Rewrote port 3000->3001" in safeguard_step["config_applied"]["arbitration_reason"]
