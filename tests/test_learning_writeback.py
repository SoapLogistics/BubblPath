import pytest
from services.solomon_learning_writeback import LearningWriteback

@pytest.fixture
def isolated_lane(tmp_path):
    db_file = tmp_path / "test_memory_atoms.db"
    return LearningWriteback(db_path=str(db_file))

def test_record_lesson_success(isolated_lane):
    res = isolated_lane.record_lesson("p1", "pass", "lesson", "We verified that timezone-aware datetimes eliminate pytest warnings.")
    assert res["recorded"] is True
    assert res.get("duplicate") is not True

def test_record_lesson_blank_rejection(isolated_lane):
    with pytest.raises(ValueError, match="Lesson content cannot be blank or empty"):
        isolated_lane.record_lesson("p1", "pass", "lesson", "")

    with pytest.raises(ValueError, match="Lesson content cannot be blank or empty"):
        isolated_lane.record_lesson("p1", "pass", "lesson", "   ")

def test_record_lesson_status_only_rejection(isolated_lane):
    with pytest.raises(ValueError, match="Lesson content cannot be status-only entries"):
        isolated_lane.record_lesson("p1", "pass", "lesson", "pass")

    with pytest.raises(ValueError, match="Lesson content cannot be status-only entries"):
        isolated_lane.record_lesson("p1", "pass", "lesson", "FAIL")

def test_record_lesson_idempotency(isolated_lane):
    packet_id = "p_idempotent_1"
    result = "pass"
    memory_type = "lesson"
    lesson_content = "This is an idempotent lesson with strict verification logic."

    # First write should succeed
    res1 = isolated_lane.record_lesson(packet_id, result, memory_type, lesson_content)
    assert res1["recorded"] is True
    assert res1.get("duplicate") is not True

    # Second identical write should return duplicate status gracefully
    res2 = isolated_lane.record_lesson(packet_id, result, memory_type, lesson_content)
    assert res2["recorded"] is True
    assert res2.get("duplicate") is True
