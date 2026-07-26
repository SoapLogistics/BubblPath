import os
from scripts.scheduler import run_scheduler
from io import StringIO
import sys

def test_loki_scheduler_disabled_by_default(monkeypatch, capsys):
    if "SOLOMON_ENABLE_LOKI_SCHEDULER" in os.environ:
        monkeypatch.delenv("SOLOMON_ENABLE_LOKI_SCHEDULER")

    run_scheduler()
    captured = capsys.readouterr()
    assert "Loki scheduler is disabled by default" in captured.out

def test_loki_scheduler_enabled(monkeypatch, capsys):
    monkeypatch.setenv("SOLOMON_ENABLE_LOKI_SCHEDULER", "1")
    run_scheduler()
    captured = capsys.readouterr()
    assert "Running Loki scheduler..." in captured.out
