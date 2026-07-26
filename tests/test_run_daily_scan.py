from scripts.run_daily_scan import run_scan

def test_deterministic_scan():
    result = run_scan(seed=42, deterministic=True)
    assert result["status"] == "success"
    assert result["deterministic"] == True
    assert result["seed"] == 42

def test_futures_scan():
    result = run_scan(mode="futures")
    assert result["status"] == "success"
    assert result["deterministic"] == True
    assert len(result["board"]) == 3
    assert result["board"][0]["threshold_class"] == "80"
    assert result["board"][1]["threshold_class"] == "90"
    assert result["board"][2]["threshold_class"] == "none"
