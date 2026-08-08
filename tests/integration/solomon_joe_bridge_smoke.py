from services.solomon_joe_bridge import JoeOmegaEngine

def test_joe_omega_dry_run():
    engine = JoeOmegaEngine()
    result = engine.queue_blueprint({"blueprint": "test_blueprint"}, run_execute=False)
    assert result["status"] == "success"
    assert result["mode"] == "dry_run"

def test_joe_omega_execution_blocked():
    engine = JoeOmegaEngine()
    result = engine.queue_blueprint({"blueprint": "test_blueprint"}, run_execute=True)
    assert result["status"] == "blocked"
    assert "Approval required" in result["reason"]
