import pytest
from services.futures.threshold_logic import calculate_confidence, evaluate_threshold

def test_80_threshold_boundary():
    assert evaluate_threshold(calculate_confidence(79.99), 80.0) == False
    assert evaluate_threshold(calculate_confidence(80.00), 80.0) == True
    assert evaluate_threshold(calculate_confidence(80.01), 80.0) == True

def test_90_threshold_boundary():
    assert evaluate_threshold(calculate_confidence(89.99), 90.0) == False
    assert evaluate_threshold(calculate_confidence(90.00), 90.0) == True
    assert evaluate_threshold(calculate_confidence(90.01), 90.0) == True
