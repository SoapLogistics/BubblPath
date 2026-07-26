import pytest
import os
import subprocess

def test_loki_scheduler_disabled_by_default():
    env = os.environ.copy()
    if "SOLOMON_ENABLE_LOKI_SCHEDULER" in env:
        del env["SOLOMON_ENABLE_LOKI_SCHEDULER"]

    result = subprocess.run(
        ["python3", "scripts/scheduler.py"],
        env=env,
        capture_output=True,
        text=True
    )

    assert "Loki scheduler is disabled by default" in result.stdout

def test_loki_scheduler_enabled():
    env = os.environ.copy()
    env["SOLOMON_ENABLE_LOKI_SCHEDULER"] = "1"

    result = subprocess.run(
        ["python3", "scripts/scheduler.py"],
        env=env,
        capture_output=True,
        text=True
    )

    assert "Running Loki scheduler..." in result.stdout

if __name__ == "__main__":
    test_loki_scheduler_disabled_by_default()
    test_loki_scheduler_enabled()
    print("Loki scheduler tests passed")
