import pytest
import os
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_embeddings import DeterministicHashProvider

@pytest.fixture
def test_db():
    db_path = "test_opt_11_20.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_exact_match_short_circuit(test_db):
    test_db.upsert_card("E1", "exact", "test", "Unique and exact search string.", is_canonical=True)
    test_db.upsert_card("E2", "exact", "test", "Something completely different entirely.", is_canonical=True)

    # Due to short-circuit, it should immediately return 1.0 similarity for E1 and only 1 result.
    res = test_db.semantic_search("Unique and exact search string.")

    assert len(res) == 1
    assert res[0]["card_id"] == "E1"
    assert res[0]["similarity"] == 1.0

def test_stopword_filtering():
    provider = DeterministicHashProvider()
    res1 = provider.embed_texts(["the and is a"])
    res2 = provider.embed_texts(["the and is a"])

    # If filtered to empty, vector[0] = 1.0 logic applies
    assert res1[0][0] == 1.0

if __name__ == "__main__":
    pytest.main(["-v", "test_embed_opts_11_20.py"])
