import pytest
from backend.services.oswald.laboratory.hypothesis_manager import HypothesisCard
from backend.services.oswald.laboratory.sandbox_manager import LaboratorySandboxManager
from backend.services.oswald.laboratory.benchmark_engine import BenchmarkEngine

def test_sandbox_experiment():
    sm = LaboratorySandboxManager()

    base_code = "print('Baseline Result: 10ms')"
    exp_code = "print('Experimental Result: 8ms')"

    results = sm.execute_experiment(exp_code, base_code)

    assert results["baseline_result"]["status"] == "success"
    assert results["experimental_result"]["status"] == "success"
    assert "STATIC ANALYSIS ONLY" in results["baseline_result"]["output"]
    assert "STATIC ANALYSIS ONLY" in results["experimental_result"]["output"]

def test_benchmark_engine():
    be = BenchmarkEngine()
    results = {
        "baseline_result": {"status": "success", "output": "time: 100"},
        "experimental_result": {"status": "success", "output": "time: 85"}
    }

    eval_result = be.evaluate(results)

    assert eval_result["conclusion"] == "SUPPORTED"
    assert eval_result["measured_improvement_pct"] == 15.0
