import pytest
import os
import sqlite3
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_topological_resolution import TopologicalResolutionEngine

@pytest.fixture
def test_db():
    db_path = "test_graph.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_topological_resolution_basic(test_db):
    test_db.upsert_card("A", "task", "core", "Task A")
    test_db.upsert_card("B", "task", "core", "Task B")
    test_db.upsert_card("C", "task", "core", "Task C")

    # A depends on B. B depends on C.
    # Expected execution sequence: C, B, A
    test_db.add_link("A", "B", "DEPENDS_ON")
    test_db.add_link("B", "C", "DEPENDS_ON")

    engine = TopologicalResolutionEngine(test_db.db_path)
    result = engine.resolve_plan(["A"])

    assert result["status"] == "success"
    assert result["execution_sequence"] == ["C", "B", "A"]
    assert not result["warnings"]

def test_topological_resolution_circular(test_db):
    test_db.upsert_card("X", "task", "core", "Task X")
    test_db.upsert_card("Y", "task", "core", "Task Y")

    # X -> Y -> X
    test_db.add_link("X", "Y", "DEPENDS_ON")
    test_db.add_link("Y", "X", "DEPENDS_ON")

    engine = TopologicalResolutionEngine(test_db.db_path)
    result = engine.resolve_plan(["X"])

    # Should resolve gracefully without infinite loop, and report warning
    assert any(w["type"] == "CIRCULAR_DEPENDENCY" for w in result["warnings"])

def test_topological_safeguards_and_conflicts(test_db):
    test_db.upsert_card("DEPLOY", "task", "deploy", "Deploy code")
    test_db.upsert_card("TESTS", "task", "test", "Run tests")
    test_db.upsert_card("PROD_CRASH", "failure", "crash", "Known crash")

    test_db.add_link("DEPLOY", "TESTS", "DEPENDS_ON")
    test_db.add_link("TESTS", "PROD_CRASH", "PREVENTS")
    test_db.add_link("DEPLOY", "PROD_CRASH", "CONFLICTS_WITH")

    engine = TopologicalResolutionEngine(test_db.db_path)
    result = engine.resolve_plan(["DEPLOY"])

    # Execution: TESTS then DEPLOY
    assert result["execution_sequence"] == ["TESTS", "DEPLOY"]

    # Safeguard from PREVENTS
    assert len(result["safeguards_injected"]) == 1
    assert result["safeguards_injected"][0]["source"] == "TESTS"
    assert result["safeguards_injected"][0]["target"] == "PROD_CRASH"

    # Conflict Warning
    assert len(result["warnings"]) == 1
    assert result["warnings"][0]["type"] == "CONFLICT"

if __name__ == "__main__":
    pytest.main(["-v", "-s", "test_topological_resolution.py"])
