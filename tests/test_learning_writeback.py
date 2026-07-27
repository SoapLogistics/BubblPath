import os
import pytest
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from services.solomon_learning_writeback import LearningWriteback

def test_record_lesson(tmp_path):
    db_path = str(tmp_path / "solomon_soss.db")
    db_manager = DatabaseManager(db_path)
    lane = LearningWriteback(db_manager=db_manager)

    # Test valid lesson
    res = lane.record_lesson("p1", "pass", "memory", "This is a valid lesson.")
    assert res["recorded"] == True

    # Test duplicate lesson
    res2 = lane.record_lesson("p1", "pass", "memory", "This is a valid lesson.")
    assert res2["recorded"] == False
    assert res2["reason"] == "duplicate"

    # Test empty lesson
    with pytest.raises(ValueError, match="Lesson cannot be blank or empty"):
        lane.record_lesson("p2", "pass", "memory", "")

    # Test status string lesson
    with pytest.raises(ValueError, match="Lesson cannot be a simple status string"):
        lane.record_lesson("p3", "pass", "memory", "pass")
