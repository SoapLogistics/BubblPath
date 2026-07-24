import pytest
from solomon_dynamic_quantization_optimizers import DynamicQuantizationOptimizer
from app import app

def test_all_50_optimizations():
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
        "grad_norm": 1.45,
        "token_sims": [0.99, 0.92, 0.98],
        "block_max": 4.0,
        "verif_latency": 100.0,
        "has_outliers": True,
        "layer_depth": 31,
        "max_depth": 32,
        "unique_weights": 50,
        "mem_limit": 4000.0,
        "mem_usage": 3900.0,
        "channel_size": 128,
        "router_conf": 0.4,
        "seq_len": 9000,
        "expert_freq": 0.02,
        "ema_max": 5.0,
        "curr_max": 10.0,
        "prev_scale": 4.0,
        "next_scale": 16.0,
        "exp_mean": 0.8,
        "quant_mean": 0.5,
        "use_stoch": True,
        "is_training": True,
        "num_elements": 1023,
        "ternary_weights": [1.0, -1.0, 0.5],
        "total_tokens": 1024,
        "quant_err": 0.5,
        "act_var": 5.0,
        "seq_access": True,
        "model_gb": 15.0,
        "ram_gb": 16.0,
        "vocab_freq": {"a": 0.1, "b": 1e-5, "c": 1e-6},
        "use_int8_embed": True,
        "head_dim": 64,
        "quant_scale": 0.5
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
