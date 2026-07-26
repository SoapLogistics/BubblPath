import os
from scripts.run_daily_scan import run_scan
from io import StringIO
import sys

def test_deterministic_scan(monkeypatch, capsys):
    monkeypatch.setenv("LOKI_SCAN_SEED", "12345")
    run_scan()
    captured = capsys.readouterr()
    assert "Running deterministic scan with seed 12345" in captured.out
