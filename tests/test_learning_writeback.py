import os
from services.solomon_learning_writeback import LearningWriteback

def test_record_lesson(tmp_path):
    test_db = os.path.join(tmp_path, "test_memory_atoms.db")
    lane = LearningWriteback(db_path=test_db)
    res = lane.record_lesson("p1", "pass", "lesson", lesson="Always normalize lookup keys before database queries")
    assert res["recorded"] == True
