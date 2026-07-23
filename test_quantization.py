"""
Unit and Integration Tests for Solomon Quantization & RAM Efficiency Optimization Engine.
"""

import json
import pytest
from app import app
from solomon_quantization_engine import (
    HessianSensitivitySolver,
    SpinQuantSimulator,
    KVCacheFootprintCalculator,
    SpeculativeDecodingPredictor
)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHessianSensitivitySolver:
    """
    Tests the second-order Hessian trace solver for Multi-Choice Knapsack budget allocation.
    """

    def test_simulated_traces(self):
        num_layers = 12
        base_params = 1e8
        traces = HessianSensitivitySolver.simulate_hessian_traces(num_layers, base_params)

        assert len(traces) == num_layers
        # Check U-shape sensitivity: Layer 0 and Layer 11 should have larger trace values than middle Layer 6
        assert traces[0]["avg_hessian_trace"] > traces[6]["avg_hessian_trace"]
        assert traces[11]["avg_hessian_trace"] > traces[6]["avg_hessian_trace"]

    def test_solve_mckp_feasible(self):
        num_layers = 8
        base_params = 8e6 # ~8 million parameters per layer
        traces = HessianSensitivitySolver.simulate_hessian_traces(num_layers, base_params)

        # Min possible size with 2-bit:
        # 8 layers * 8M params * 2 bits / (8 * 1e6) = 16 MB approx.
        # Let's provide a budget that allows mixed-precision upgrades
        target_budget = 40.0 # MB

        result = HessianSensitivitySolver.solve_mckp(traces, target_budget)
        assert result["feasible"] is True
        assert result["total_size_mb"] <= target_budget
        assert len(result["allocations"]) == num_layers
        for alloc in result["allocations"]:
            assert alloc["bit_width"] in [2, 3, 4, 5, 6, 8]

    def test_solve_mckp_infeasible_fallback(self):
        num_layers = 4
        base_params = 1e8 # massive layers
        traces = HessianSensitivitySolver.simulate_hessian_traces(num_layers, base_params)

        # Min possible size is 4 * 100M * 2 bits / (8 * 1024 * 1024) = 95.36 MB
        # Provide a budget that is far too low
        target_budget = 10.0 # MB

        result = HessianSensitivitySolver.solve_mckp(traces, target_budget)
        assert result["feasible"] is False
        assert "Falling back" in result["message"]
        # Allocations should still be returned, all defaulted to minimum 2-bit
        for alloc in result["allocations"]:
            assert alloc["bit_width"] == 2


class TestSpinQuantSimulator:
    """
    Tests the SpinQuant orthogonal learned rotations simulation.
    """

    def test_outlier_suppression(self):
        initial_outliers = 100

        # Without SpinQuant
        result_without = SpinQuantSimulator.simulate_rotation_outlier_reduction(initial_outliers, use_spinquant=False)
        assert result_without["outliers_retained"] == initial_outliers
        assert result_without["outlier_suppression_ratio"] == 1.0
        assert result_without["recommended_bit_width"] == 8

        # With SpinQuant
        result_with = SpinQuantSimulator.simulate_rotation_outlier_reduction(initial_outliers, use_spinquant=True)
        assert result_with["outliers_retained"] < initial_outliers
        assert result_with["outlier_suppression_ratio"] > 10.0
        assert result_with["recommended_bit_width"] == 4


class TestKVCacheFootprintCalculator:
    """
    Tests Key-Value Cache sizing and memory fragmentation comparisons.
    """

    def test_calculate_footprint_precisions(self):
        # Setup small transformer dimensions
        batch_size = 2
        context_len = 1024
        num_layers = 16
        num_heads = 8
        head_dim = 64

        # FP16 Size: Elements = 2 * 2 * 1024 * 16 * 8 * 64 = 33,554,432 elements
        # bytes = 33,554,432 * 2 = 67,108,864 bytes = 64.0 MB
        fp16_result = KVCacheFootprintCalculator.calculate_footprint(
            batch_size, context_len, num_layers, num_heads, head_dim, "FP16"
        )
        assert fp16_result["raw_cache_size_mb"] == 64.0

        # INT8 is exactly half of FP16 (32.0 MB)
        int8_result = KVCacheFootprintCalculator.calculate_footprint(
            batch_size, context_len, num_layers, num_heads, head_dim, "INT8"
        )
        assert int8_result["raw_cache_size_mb"] == 32.0

        # INT4 is exactly quarter of FP16 (16.0 MB)
        int4_result = KVCacheFootprintCalculator.calculate_footprint(
            batch_size, context_len, num_layers, num_heads, head_dim, "INT4"
        )
        assert int4_result["raw_cache_size_mb"] == 16.0


class TestSpeculativeDecodingPredictor:
    """
    Tests speculative decoding speedup and efficiency multipliers.
    """

    def test_predict_performance(self):
        target_size_gb = 14.0
        draft_size_gb = 0.7
        acceptance_rate = 0.8

        result = SpeculativeDecodingPredictor.predict_performance(
            target_model_size_gb=target_size_gb,
            draft_model_size_gb=draft_size_gb,
            acceptance_rate=acceptance_rate,
            draft_generation_latency_ms=10.0,
            target_verification_latency_ms=50.0,
            num_speculated_tokens=5
        )

        assert result["expected_tokens_verified"] > 1.0
        assert result["throughput_speedup_factor"] > 1.0
        assert result["combined_ram_requirement_gb"] == 14.7


class TestFlaskAPIIntegration:
    """
    Integration tests verifying the Flask API routes, outputs, and validation rules.
    """

    def test_get_blueprint(self, client):
        response = client.get("/api/quantization/blueprint")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "active"
        assert "blueprint_title" in data
        assert "core_components" in data
        assert "sensivity_score" in data["mathematical_formulations"]

    def test_post_simulate_success(self, client):
        payload = {
            "model_size_params": 1e9, # 1 Billion parameter model
            "num_layers": 8,
            "target_ram_mb": 500.0, # 500MB target
            "batch_size": 2,
            "context_len": 512,
            "use_spinquant": True
        }
        response = client.post(
            "/api/quantization/simulate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "hessian_mixed_precision_solver" in data
        assert "kv_cache_compression" in data
        assert "speculative_decoding_prediction" in data
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]

    def test_post_simulate_invalid_params(self, client):
        # Send non-numeric layer count to trigger validation failure
        payload = {
            "num_layers": "invalid_string_layer",
            "target_ram_mb": 1000.0
        }
        response = client.post(
            "/api/quantization/simulate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_get_cognitive_cycle(self, client):
        """
        Asserts that the GET /api/quantization/cognitive-cycle endpoint returns an
        HTTP 200 status code and the correct JSON schema with fields matching the SOK card families.
        """
        response = client.get("/api/quantization/cognitive-cycle")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "active"
        assert len(data["seven_stages_sequence"]) == 7

        cards = data["sok_card_families"]
        assert cards["SOK-MISSION-QUANT-001"]["family"] == "Mission"
        assert cards["SOK-PROCEDURE-QUANT-001"]["family"] == "Procedure"
        assert cards["SOK-TASK-QUANT-001"]["family"] == "Task"
        assert cards["SOK-EXECUTION-QUANT-001"]["family"] == "Execution"
        assert cards["SOK-REVIEW-QUANT-001"]["family"] == "Review"
        assert cards["SOK-KNOWLEDGE-QUANT-001"]["family"] == "Knowledge"
        assert cards["SOK-IMPROVED-PROCEDURE-QUANT-001"]["family"] == "Improved Procedure"
        assert "RECOMMENDED NEXT STEP" in data["recommended_next_step"]
