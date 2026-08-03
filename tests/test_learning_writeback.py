from services.solomon_learning_writeback import LearningWriteback

def test_record_lesson():
    lane = LearningWriteback()
    res = lane.record_lesson("p1", "pass", "lesson")
    assert res["recorded"]
