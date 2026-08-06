import json
import os
import tempfile

from app import app

# Import target components
from gabriel_engine.core.ast_injector import ASTCodeInjector
from gabriel_engine.core.observational_simulator import ObservationalSandboxSimulator
from gabriel_engine.core.recursive_optimizer import RecursiveCrucibleOptimizer


def test_ast_code_injector():
    """
    Asserts AST modifications can inject new method logic programmatically.
    """
    dummy_source = """class DummyAgent:
    def greet(self):
        return "hello"
"""
    function_to_inject = """def ask_solomon(self, question):
    return f"answering: {question}"
"""

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(dummy_source)
        temp_path = f.name

    try:
        # Inject method using AST Code Injector
        ASTCodeInjector.inject_function_to_class(
            file_path=temp_path,
            class_name="DummyAgent",
            function_source=function_to_inject
        )

        with open(temp_path, "r") as f:
            updated_source = f.read()

        # Compile and execute the dynamically mutated class!
        local_vars = {}
        exec(updated_source, local_vars)
        DummyAgentClass = local_vars["DummyAgent"]

        agent = DummyAgentClass()
        assert agent.greet() == "hello"
        assert agent.ask_solomon("who is gabriel?") == "answering: who is gabriel?"

    finally:
        os.remove(temp_path)


def test_recursive_optimization_feedback():
    """
    Asserts that recursive feedback refactors slow loop code.
    """
    slow_code = """class ExponentialBackoffRetry:
    def __init__(self):
        self.base_delay = 0.5
"""
    metrics = {
        "average_latency_ms": 350.0,
        "errors_logged": 2,
        "completion_rate": 0.85
    }

    optimizer = RecursiveCrucibleOptimizer()
    opt_code, opt_metrics, rounds = optimizer.optimize_code(
        capability_name="exponential_backoff_retry",
        original_code=slow_code,
        crucible_metrics=metrics,
        target_latency_ms=100.0,
        max_recursive_rounds=2
    )

    assert rounds > 0
    assert opt_metrics["average_latency_ms"] < 250.0
    assert opt_metrics["errors_logged"] == 0
    assert "class TokenBucketThrottler" in opt_code


def test_observational_sandbox_simulator():
    """
    Asserts closed binary observational profiling produces blueprint specifications.
    """
    simulator = ObservationalSandboxSimulator()
    res = simulator.deconstruct_binary("docker-cli")

    assert res["target"] == "docker-cli"
    assert "behavioral_rebuild_spec" in res
    assert "OBSERVED REST INTERFACES" in res["behavioral_rebuild_spec"]
    assert "inferred_architecture" in res


def test_evolutionary_api_endpoints():
    """
    Asserts REST routing endpoints work seamlessly.
    """
    client = app.test_client()

    # 1. Test Observe & Deconstruct
    res_obs = client.post("/api/gabriel/observe", json={
        "binary_name": "kubernetes-cli"
    })
    assert res_obs.status_code == 200
    data_obs = json.loads(res_obs.data)
    assert data_obs["status"] == "success"
    assert data_obs["binary_deconstructed"] == "kubernetes-cli"

    # 2. Test Optimize Endpoint
    res_opt = client.post("/api/gabriel/optimize", json={
        "capability_name": "worker_lease",
        "original_code": "class Lease:\n    def __init__(self):\n        self.lease_duration_sec: int = 10",
        "crucible_metrics": {
            "average_latency_ms": 400.0,
            "errors_logged": 1
        },
        "target_latency_ms": 100.0
    })
    assert res_opt.status_code == 200
    data_opt = json.loads(res_opt.data)
    assert data_opt["status"] == "success"
    assert "optimized_code" in data_opt
    assert "lease_duration_sec: int = 2" in data_opt["optimized_code"]

    # 3. Test AST Inject Endpoint
    dummy_source = "class TargetModel:\n    pass\n"
    func_source = "def predict(self):\n    return 1.0\n"

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(dummy_source)
        temp_path = f.name

    try:
        res_ast = client.post("/api/gabriel/ast-inject", json={
            "file_path": temp_path,
            "class_name": "TargetModel",
            "function_source": func_source
        })
        assert res_ast.status_code == 200
        data_ast = json.loads(res_ast.data)
        assert data_ast["status"] == "success"

        with open(temp_path, "r") as f:
            mutated_code = f.read()
        assert "def predict(self):" in mutated_code
    finally:
        os.remove(temp_path)
