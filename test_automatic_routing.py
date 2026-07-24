import pytest
from solomon_automatic_routing import AutomaticRoutingEngine

def test_automatic_routing_engine():
    engine = AutomaticRoutingEngine()

    ram_usage = engine.measure_ram_usage(num_parameters=7e9, precision_bits=4, context_tokens=1024)
    assert ram_usage > 0.0

    latency = engine.benchmark_latency(num_parameters=7e9, precision_bits=4, context_tokens=1024)
    assert latency > 0.0

    accuracy = engine.benchmark_accuracy(num_parameters=7e9, precision_bits=4, context_tokens=1024)
    assert accuracy > 0.0

    thresholds = engine.determine_routing_thresholds(available_ram_mb=1500.0, target_latency_ms=15.0, target_accuracy=85.0)
    assert "dynamic_threshold" in thresholds
    assert thresholds["dynamic_threshold"] > 0.15 # Should increase due to low RAM and tight latency

    scenarios = engine.identify_where_quantized_models_can_replace_full_precision(available_ram_mb=1500.0)
    assert len(scenarios) > 0
    assert "Low RAM environments (< 4GB)" in scenarios

    decision = engine.create_automatic_routing_logic("What is the capital of France?", available_ram_mb=1500.0, target_latency_ms=15.0, target_accuracy=85.0)
    assert decision["routing_decision"] is not None
    assert decision["applied_threshold"] == thresholds["dynamic_threshold"]
