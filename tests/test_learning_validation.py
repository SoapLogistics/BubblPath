import os
import pytest
from services.solomon_learning_writeback import LearningWriteback

def test_rejects_empty_lesson(tmp_path):
    test_db = os.path.join(tmp_path, "test_memory_atoms.db")
    lane = LearningWriteback(db_path=test_db)

    with pytest.raises(ValueError, match="cannot be empty"):
        lane.record_lesson("p1", "pass", "lesson", lesson="")

def test_rejects_status_only_lesson(tmp_path):
    test_db = os.path.join(tmp_path, "test_memory_atoms.db")
    lane = LearningWriteback(db_path=test_db)

    with pytest.raises(ValueError, match="cannot be a status-only word"):
        lane.record_lesson("p1", "pass", "lesson", lesson="pass")

def test_idempotency_prevents_duplicates(tmp_path):
    test_db = os.path.join(tmp_path, "test_memory_atoms.db")
    lane = LearningWriteback(db_path=test_db)

    # First write
    res1 = lane.record_lesson("p1", "pass", "lesson", lesson="Always normalize keys before lookup")
    assert res1["recorded"] is True
    assert res1["duplicate"] is False

    # Second write (same content)
    res2 = lane.record_lesson("p1", "pass", "lesson", lesson="Always normalize keys before lookup")
    assert res2["recorded"] is True
    assert res2["duplicate"] is True
