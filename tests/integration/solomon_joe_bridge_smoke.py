from services.solomon_joe_bridge import JoeOmegaEngine

def test_solomon_joe_bridge_blocked():
    engine = JoeOmegaEngine()
    result = engine.queue_blueprint("test_data", run_execute=True)
    assert result["status"] == "blocked"
    assert result["reason"] == "Approval required for execution"
