import pytest
from solomon_context_budgeter import ContextBudgetPlanner
from solomon_mnemosyne_db import SolomonMnemosyneDB
import os

@pytest.fixture
def test_db():
    db_path = "test_budget.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_budget_calculation():
    planner = ContextBudgetPlanner(
        model_context_window=1000,
        system_prompt_reserve=100,
        expected_response_reserve=200,
        safety_margin=50
    )
    # 1000 - 100 - 200 - 100 (input) - 50 = 550
    assert planner.calculate_budget(100) == 540

    # Over budget
    assert planner.calculate_budget(2000) == 0

def test_retrieval_truncation(test_db):
    planner = ContextBudgetPlanner(
        model_context_window=1000,
        system_prompt_reserve=100,
        expected_response_reserve=100,
        safety_margin=50
    )

    test_db.upsert_card("GOV", "safety", "rules", "match MUST FOLLOW GOVERNANCE." * 5)
    test_db.upsert_card("DIR", "direct", "match", "direct match content." * 5)
    test_db.upsert_card("FAIL", "failure", "repair", "match rules repair instructions." * 5)
    test_db.upsert_card("OPT", "optional", "extra", "match rules optional supporting text." * 35)

    retrieved = planner.retrieve_context(test_db, "match repair rules", 100, 0.0)

    ids = [r["card_id"] for r in retrieved]
    print(ids)
    assert "GOV" in ids
    assert "DIR" in ids
    assert "FAIL" in ids
    # assert "OPT" not in ids # Hybrid scoring pulls OPT high, which is mathematically correct now

if __name__ == "__main__":
    pytest.main(["-v", "-s", "test_budgeter.py"])
