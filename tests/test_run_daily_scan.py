from scripts.run_daily_scan import run_scan

def test_deterministic_scan():
    result = run_scan(seed=42, deterministic=True)
    assert result["status"] == "success"
    assert result["deterministic"] == True
    assert result["seed"] == 42
import os

def test_futures_scan_disabled():
    os.environ["SOLOMON_ENABLE_LOKI_SCHEDULER"] = "0"
    result = run_scan(mode="futures")
    assert result["status"] == "error"

def test_futures_scan_enabled():
    os.environ["SOLOMON_ENABLE_LOKI_SCHEDULER"] = "1"
    result = run_scan(mode="futures")
    assert result["status"] == "success"
    assert len(result["data"]) > 0
