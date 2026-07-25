import pytest
import os
from solomon_metrics import SolomonMetricsEngine
from solomon_learning_engine import HolographicLearningCore

@pytest.fixture
def temp_metrics_file(tmp_path):
    file_path = tmp_path / "test_metrics.bin"
    return str(file_path)

def test_metrics_engine(temp_metrics_file):
    engine = SolomonMetricsEngine(max_records=10, file_path=temp_metrics_file)
    engine.record_interaction(10.5, True, 0.9, 0.2, "/test", "payload")
    records = engine.get_all_records()
    assert len(records) == 1
    assert records[-1]["endpoint"] == "/test"
    assert records[-1]["success"] is True
    engine.close()

def test_learning_core(temp_metrics_file):
    engine = SolomonMetricsEngine(max_records=10, file_path=temp_metrics_file)
    # Inject record specifically for this test to be independent
    engine.record_interaction(1.2, True, 0.8, 0.5, "/system/run-learning-cycle", "run_cycle")

    core = HolographicLearningCore(engine)
    result = core.execute_learning_cycle()
    assert result["status"] == "success"
    assert "optimizations" in result
    assert result["records_analyzed"] == 1
    engine.close()
