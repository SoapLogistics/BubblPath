import pytest
import os
from solomon_mnemosyne_db import SolomonMnemosyneDB

@pytest.fixture
def test_db():
    db_path = "test_opt_1_10.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_batched_upserts(test_db):
    cards = [
        {"card_id": "B1", "family": "batch", "focus": "test", "content": "Batch 1"},
        {"card_id": "B2", "family": "batch", "focus": "test", "content": "Batch 2"},
        {"card_id": "B3", "family": "batch", "focus": "test", "content": "Batch 3"}
    ]
    assert test_db.upsert_cards_batch(cards) == 3
    assert test_db.get_card("B2")["content"] == "Batch 2"

def test_fts5_sync(test_db):
    test_db.upsert_card("F1", "fts", "search", "The quick brown fox jumps over the lazy dog.")

    import sqlite3
    conn = sqlite3.connect(test_db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id FROM knowledge_cards_fts WHERE content MATCH 'fox'")
    res = cursor.fetchone()
    conn.close()

    assert res is not None
    assert res[0] == "F1"

if __name__ == "__main__":
    pytest.main(["-v", "test_db_optimizations_1_10.py"])
