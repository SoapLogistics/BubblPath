from gabriel_engine.learning.feedback.feedback_loop import FeedbackLoop

def test_feedback_loop():
    loop = FeedbackLoop()
    result = loop.route_feedback({"test": "data"})
    assert result is True
