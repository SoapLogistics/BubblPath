import pytest
import os
from services.solomon_futures_engine import FuturesEngine

def test_threshold_logic_80(tmp_path):
    log_file = os.path.join(tmp_path, "test_fact_memory.log")
    engine = FuturesEngine(log_file=log_file)

    # Boundary tests
    assert engine.evaluate_threshold(79.99, 80.0) is False
    assert engine.evaluate_threshold(80.00, 80.0) is True
    assert engine.evaluate_threshold(80.01, 80.0) is True

def test_threshold_logic_90(tmp_path):
    log_file = os.path.join(tmp_path, "test_fact_memory.log")
    engine = FuturesEngine(log_file=log_file)

    # Boundary tests
    assert engine.evaluate_threshold(89.99, 90.0) is False
    assert engine.evaluate_threshold(90.00, 90.0) is True
    assert engine.evaluate_threshold(90.01, 90.0) is True

def test_invalid_threshold(tmp_path):
    log_file = os.path.join(tmp_path, "test_fact_memory.log")
    engine = FuturesEngine(log_file=log_file)
    with pytest.raises(ValueError):
        engine.evaluate_threshold(85.0, 85.0)

def test_projection_shape(tmp_path):
    log_file = os.path.join(tmp_path, "test_fact_memory.log")
    engine = FuturesEngine(log_file=log_file)
    proj = engine.generate_projection("game_1", 90.0, {"team": "A"})

    assert "target_id" in proj
    assert "confidence" in proj
    assert "threshold_80_met" in proj
    assert "threshold_90_met" in proj
    assert "data_health" in proj
    assert proj["data_health"] == "verified"
    assert proj["threshold_90_met"] is True
    assert proj["threshold_80_met"] is True

    proj_marginal = engine.generate_projection("game_2", 79.99, {"team": "B"})
    assert proj_marginal["data_health"] == "marginal"
    assert proj_marginal["threshold_80_met"] is False
    assert proj_marginal["threshold_90_met"] is False

def test_fact_memory_logging(tmp_path):
    log_file = os.path.join(tmp_path, "test_fact_memory.log")
    engine = FuturesEngine(log_file=log_file)
    engine.evaluate_threshold(90.5, 90.0)

    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        content = f.read()
        assert "Threshold 90.0 crossed" in content
