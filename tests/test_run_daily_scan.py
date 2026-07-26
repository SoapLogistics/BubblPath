from scripts.run_daily_scan import run_scan

def test_deterministic_scan():
    result = run_scan(seed=42, deterministic=True)
    assert result["status"] == "success"
    assert result["deterministic"] == True
    assert result["seed"] == 42
