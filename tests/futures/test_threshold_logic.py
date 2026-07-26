import pytest
from core.futures.futures_engine import evaluate_thresholds

def test_80_boundary():
    res = evaluate_thresholds(79.99, 50.0, 50.0)
    assert not res["breached_80"]
    assert not res["is_80_confidence"]

    res = evaluate_thresholds(80.00, 50.0, 50.0)
    assert res["breached_80"]
    assert res["is_80_confidence"]

def test_90_boundary():
    res = evaluate_thresholds(89.99, 50.0, 50.0)
    assert not res["breached_90"]
    assert not res["is_90_confidence"]

    res = evaluate_thresholds(90.00, 50.0, 50.0)
    assert res["breached_90"]
    assert res["is_90_confidence"]

def test_all_metrics():
    res = evaluate_thresholds(50.0, 80.0, 50.0)
    assert res["breached_80"]
    assert res["is_80_probability"]

    res = evaluate_thresholds(50.0, 50.0, 90.0)
    assert res["breached_90"]
    assert res["is_90_performance"]
