import pytest
import os
from services.solomon_continuous_optimizer import ContinuousOptimizationEngine

def test_continuous_optimization_engine():
    engine = ContinuousOptimizationEngine()

    payload = {
        "a": 1,
        "b": None,
        "c": "test"
    }

    result = engine.optimize_payload(payload)

    assert result["status"] == "optimized"
    assert result["original_keys"] == 3
    assert result["compressed_keys"] == 2

    # Cleanup memory mapped file
    engine.budget.close()
    if os.path.exists("quantized_budget.bin"):
        os.remove("quantized_budget.bin")
