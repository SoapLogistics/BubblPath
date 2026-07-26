import pytest
from services.solomon_joe_bridge import JoeOmegaEngine

def test_joe_omega_dry_run():
    engine = JoeOmegaEngine()
    result = engine.queue_blueprint({"name": "test"}, run_execute=False)
    assert result["mode"] == "dry_run"

def test_joe_omega_refusal():
    engine = JoeOmegaEngine()
    result = engine.queue_blueprint({"name": "test"}, run_execute=True)
    assert result["status"] == "blocked"
    assert "Approval required" in result["reason"]

if __name__ == "__main__":
    test_joe_omega_dry_run()
    test_joe_omega_refusal()
    print("Joe smoke tests pass")
