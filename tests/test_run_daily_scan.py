from scripts.run_daily_scan import run_scan

def test_deterministic_scan():
    # Adjusted to match the new strict signature representing SHADOW/TEST modes
    result = run_scan(mode="TEST", seed=42)
    assert result["mode"] == "TEST"
    assert "stats" in result
