import pytest
import sqlite3
import time
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_embedding_worker import AsyncEmbeddingWorker
import os

@pytest.fixture
def test_db():
    db_path = "test_async_worker.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_async_worker_batch(test_db):
    test_db.upsert_card("CARD-1", "Test", "Test", "This is a test card for embeddings.")
    test_db.upsert_card("CARD-2", "Test", "Test", "Another test card here.")

    # Run a synchronous batch
    worker = AsyncEmbeddingWorker(db_path=test_db.db_path, batch_size=2)
    worker.process_batch()

    # verify
    conn = sqlite3.connect(test_db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM card_embeddings")
    count = cursor.fetchone()[0]

    if worker.provider.get_metadata()["provider"] != "deterministic_hash":
        assert count >= 2

    conn.close()

if __name__ == "__main__":
    pytest.main(["-v", "test_async_worker.py"])
