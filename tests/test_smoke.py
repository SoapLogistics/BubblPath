from services.soss_workspace_status import SossWorkspaceStatus
from services.solomon_joe_bridge import JoeOmegaEngine
from services.system_events import SystemEvents

def test_soss_workspace_status_smoke():
    assert SossWorkspaceStatus().get_status()["status"] == "ok"

def test_joe_bridge_smoke():
    assert JoeOmegaEngine().get_status()["status"] == "ready"

def test_system_events_smoke():
    assert SystemEvents().emit("test") is True
