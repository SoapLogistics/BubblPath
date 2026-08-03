import pytest
import os
from gabriel_engine.core.perpetual_loop import GabrielPerpetualLoop
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.api.repository import CardRepository
from core.solomon_knowledge_cards.planner.engine import DynamicPlanner

@pytest.fixture
def setup_env():
    db_path = "test_learning_loop.sqlite"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ["MNEMOSYNE_DB_PATH"] = db_path

    yield db_path

    if os.path.exists(db_path):
        os.remove(db_path)
    if "MNEMOSYNE_DB_PATH" in os.environ:
        del os.environ["MNEMOSYNE_DB_PATH"]

def test_closed_learning_loop(setup_env):
    """
    Tests the closed learning loop:
    1. Run mission (assimilate project).
    2. Capture learning record.
    3. Persist to DB.
    4. Have the planner retrieve and use it to change a plan.
    5. Test contradiction.
    """
    db_path = setup_env
    loop = GabrielPerpetualLoop()

    # 1. Run mission 1
    # Create a mock decision override so it succeeds and generates a learning record
    overrides = {
        "value": 5.0,
        "reliability": 5.0,
        "compatibility": 5.0,
        "maintainability": 5.0
    }

    # This will generate learning records internally in STAGE 10
    result = loop.assimilate_project("test_mission_1", "/dummy/path", decision_overrides=overrides)

    # 2. Check if learning record was captured in loop log
    assert result["loop_learning_summary"].get("learning_records_generated", 0) > 0, "No learning records were generated."

    # 3. Use Planner to query Mnemosyne
    # We should see the new learning record influence the plan
    db_manager = DatabaseManager(db_path)
    repository = CardRepository(db_manager)
    planner = DynamicPlanner(repository)

    # Since we know the capabilities were extracted and learned from, let's look at the cards
    cards = db_manager.list_all_cards()
    lesson_cards = [c for c in cards if c.card_type == "LESSON"]
    assert len(lesson_cards) > 0, "No LESSON cards persisted to DB."

    # Check if a lesson influences a plan
    procedure_id = lesson_cards[0].extra_metadata.get("procedure_id", "unknown")
    plan = planner.draft_plan("TASK_01", f"Use {procedure_id}")

    # We should see a step mentioning the LEARNED PROCEDURE or PRE-EMPTIVE SAFEGUARD
    step_found = False
    for step in plan.steps:
        if procedure_id in step["action"] and ("LEARNED PROCEDURE" in step["action"] or "PRE-EMPTIVE SAFEGUARD" in step["action"]):
            step_found = True
            break

    assert step_found, f"Planner did not use learning record for {procedure_id}"

    # 4. Run mission 2 with failures to test contradiction
    # By forcing a low value and failing status, we create a contradiction
    loop.native_implementations = {} # Clear implementations
    loop.capability_cards = {}

    # Force failure by overriding decision engine to always choose WRAP, but registry to throw error
    overrides_fail = {
        "value": 5.0, # ensure it tries to process
        "reliability": 5.0,
        "compatibility": 5.0,
        "maintainability": 5.0
    }
    class FailingRegistry:
        def register_and_save(self, name, code):
            raise Exception("Forced failure")
        def load_capability(self, name):
            pass
    loop.registry = FailingRegistry()

    result2 = loop.assimilate_project("test_mission_2", "/dummy/path", decision_overrides=overrides_fail)

    # Retrieve updated card to check contradiction
    cards_after = db_manager.list_all_cards()
    lesson_cards_after = [c for c in cards_after if c.card_type == "LESSON"]

    target_card = None
    for c in lesson_cards_after:
        if c.extra_metadata.get("procedure_id") == procedure_id:
            target_card = c
            break

    assert target_card is not None
    assert len(target_card.extra_metadata.get("contradicting_evidence", [])) > 0, "Contradicting evidence not recorded."
    assert target_card.confidence < lesson_cards[0].confidence, "Confidence was not lowered due to contradiction."
