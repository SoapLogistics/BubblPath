import pytest
import os
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_topological_resolution import TopologicalResolutionEngine

@pytest.fixture
def test_db():
    db_path = "test_opt_31_40.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_explainability_tree(test_db):
    test_db.upsert_card("N1", "familyA", "focus", "ContentA")
    test_db.upsert_card("N2", "familyB", "focus", "ContentB")
    test_db.add_link("N1", "N2", "DEPENDS_ON")

    engine = TopologicalResolutionEngine(test_db.db_path)
    res = engine.resolve_plan(["N1"])

    # Check that explanation is dict tree
    assert len(res["explanations"]) == 1
    assert res["explanations"][0]["action"] == "dependency_chain"
    assert res["explanations"][0]["source"] == "N1"

if __name__ == "__main__":
    pytest.main(["-v", "test_topo_opts_31_40.py"])
