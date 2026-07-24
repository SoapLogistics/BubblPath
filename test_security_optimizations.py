import pytest
import os
from solomon_db_snapshot import DBSnapshotManager
from solomon_mnemosyne_db import SolomonMnemosyneDB

@pytest.fixture
def test_db():
    db_path = "test_sec.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = SolomonMnemosyneDB(db_path=db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_db_snapshot_rollback(test_db):
    test_db.upsert_card("S1", "test", "snapshot", "Original state")

    manager = DBSnapshotManager(test_db.db_path)
    assert manager.take_snapshot()

    # "Catastrophic failure" alters db
    test_db.upsert_card("S1", "test", "snapshot", "Corrupted state!")
    assert test_db.get_card("S1")["content"] == "Corrupted state!"

    # Rollback
    assert manager.restore_snapshot()

    # Verify original state is back
    # Re-init db object to bust any cache though Python SQLite handles it
    db2 = SolomonMnemosyneDB(db_path=test_db.db_path)
    assert db2.get_card("S1")["content"] == "Original state"
    manager.cleanup()

if __name__ == "__main__":
    pytest.main(["-v", "test_security_optimizations.py"])
