import pytest
import os
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_context_budgeter import ContextBudgetPlanner

@pytest.fixture
def test_db():
    db_path = "test_opt_21_30.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_sliding_window_truncation(test_db):
    planner = ContextBudgetPlanner(
        model_context_window=500,
        system_prompt_reserve=100,
        expected_response_reserve=100,
        safety_margin=50
    )

    test_db.upsert_card("HUGE", "direct", "match", "A" * 1400)

    # task size = 100
    # Budget: 1000 - 100 - 100 - 100 - (50 + 10) = 640 tokens
    # 5000 chars is ~1428 tokens, which exceeds 640.
    # Opt 22 should truncate it to fit EXACTLY 640 tokens (~2240 chars)

    res = planner.retrieve_context(test_db, "match", 100, 0.0)

    assert len(res) == 1
    assert "[TRUNCATED]" in res[0]["content"]
    assert len(res[0]["content"]) < 3000

if __name__ == "__main__":
    pytest.main(["-v", "test_budgeter_opts_21_30.py"])
