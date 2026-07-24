import pytest
from solomon_dynamic_quantization_optimizers import DynamicQuantizationOptimizer
from app import app

def test_all_25_optimizations():
    payload = {
        "entropy": 0.9,
        "attention_scores": [0.1, 0.02, 0.5],
        "target_bits": 8,
        "is_base_model": True,
        "context_length": 4096,
        "activations": [0.01, 0.5, 1.0],
        "quant_noise": 0.2,
        "layer_index": 1,
        "weight_variance": 0.8,
        "batch_mean": 0.3,
        "gradients": [0.5, 0.5],
        "channel_variances": [0.1, 0.8],
        "token_index": 2,
        "act_max": 20.0,
        "weight_max": 5.0,
        "layer_type": "linear",
        "token_complexity": 0.9,
        "group_size": 100,
        "weights": [0.001, 0.8],
        "channel_mags": [0.1, 0.2, 0.3, 0.4, 10.0],
        "domain": "medical",
        "memory_pressure": 0.98,
        "identity_sim": 0.999,
        "grad_norm": 1.45
    }

    results = DynamicQuantizationOptimizer.apply_all_optimizations(payload)

    assert results["step_1_entropy_bits"] == 8
    assert results["step_2_kv_eviction_len"] == 2
    assert results["step_3_draft_bits"] == 4
    assert results["step_4_lora_bits"] == 4
    assert results["step_5_rope_scale"] == 2.0
    assert results["step_7_temp"] == 0.6
    assert results["step_8_kv_bits"] == 16
    assert results["step_10_group_size"] == 64
    assert results["step_11_zp_shift"] == -0.3
    assert results["step_13_channel_scale"] is True
    assert results["step_14_keep_sink"] is True
    assert results["step_15_smoothquant"] == 2.0
    assert results["step_16_use_nf4"] is True
    assert results["step_17_token_bits"] == 8
    assert results["step_18_padded_group"] == 128
    assert results["step_21_calib_set"] == "calibration_set_medical"
    assert results["step_23_recompute"] is True
    assert results["step_24_drop_layer"] is True
    assert results["step_25_grad_quant"] == 1.4

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_dynamic_optimize_endpoint(client):
    response = client.post("/api/command-center/quantization/dynamic-optimize", json={"entropy": 0.2})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "optimization_results" in data
    assert data["optimization_results"]["step_1_entropy_bits"] == 4
