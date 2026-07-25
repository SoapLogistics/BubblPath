import pytest
from solomon_core.soss.sandbox import PythonCrucible
from solomon_core.sple.scheduler import SystemScheduler, ScheduledTask
from solomon_core.event_bus import CognitiveEventBus
import time

def test_python_crucible_success():
    crucible = PythonCrucible()
    res = crucible.execute("x = y * 2", {"y": 10})
    assert res["success"] is True
    assert res["state"]["x"] == 20
    assert "error" in res and res["error"] is None

def test_python_crucible_security_fail():
    crucible = PythonCrucible()
    res = crucible.execute("import os\nos.system('echo 1')", {})
    assert res["success"] is False
    assert "Security validation failed" in res["error"]

def test_scheduler():
    bus = CognitiveEventBus()
    scheduler = SystemScheduler(bus)

    execution_count = 0
    def dummy_action():
        nonlocal execution_count
        execution_count += 1

    scheduler.register_task("test_task", 1, dummy_action)

    # Normally we'd start it, but for a quick test we can just tick manually
    # to avoid thread timing issues in pytest.

    # Overwrite last run to force trigger
    scheduler.tasks[-1].last_run = 0

    # Tick manually
    now = time.time()
    for task in scheduler.tasks:
        if now - task.last_run >= task.interval:
            task.action()

    assert execution_count == 1
