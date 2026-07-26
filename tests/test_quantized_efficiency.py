import pytest
import os
import time
from core.solomon_quantized_efficiency import QuantizedEngineBudget, Tier, measure_efficiency, RuntimeGuardrails

def test_quantized_engine_budget():
    budget = QuantizedEngineBudget(filename="test_quantized_budget.bin", max_entries=10)

    budget.record_usage("test_engine", Tier.T1_deterministic_for_dry_run, 10.5, 100.0)
    budget.record_usage("another_engine", Tier.T2_stateless_service, 20.0, 50.0)

    # In a real test, we might check the file contents, but for now we just make sure it doesn't crash
    # and the file is created.
    assert os.path.exists("test_quantized_budget.bin")

    budget.close()
    if os.path.exists("test_quantized_budget.bin"):
        os.remove("test_quantized_budget.bin")

def test_measure_efficiency():
    @measure_efficiency
    def slow_function():
        time.sleep(0.01)
        return "done"

    result, duration = slow_function()
    assert result == "done"
    assert duration >= 0.01

def test_runtime_guardrails():
    guardrails = RuntimeGuardrails(max_memory_mb=64, max_cpu_time_sec=5.0)
    assert guardrails.max_memory_mb == 64
    assert guardrails.max_cpu_time_sec == 5.0
    assert guardrails.allowed_network is False
    assert guardrails.allowed_fs is False
