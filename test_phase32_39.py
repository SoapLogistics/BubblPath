import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_phase_20_context_budget(client):
    """
    1. Test SOSS Phase 20 dynamic context budget calculation.
    """
    res = client.post("/api/command-center/context/budget", json={
        "available_ram_gb": 2.0
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["phase"] == "SOSS Phase 20 (Dynamic Context Budgeter)"
    assert data["max_character_budget"] == 20971520


def test_phase_32_ternary_entropy(client):
    """
    2. Test SOSS Phase 32 ternary entropy calculation.
    """
    res = client.post("/api/quantization/ternary-entropy", json={
        "layer_weights": [0.5, -0.2, 0.1, -0.9]
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["phase"] == "SOSS Phase 32 (Ternary Entropy)"
    assert data["ternary_entropy_bits"] > 0.0


def test_phase_23_speculative_throughput(client):
    """
    3. Test SOSS Phase 23 speculative decoding throughput predictor.
    """
    res = client.post("/api/quantization/speculative/throughput", json={
        "target_throughput": 40.0,
        "speedup_factor": 2.1
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["speculative_throughput_tokens_sec"] == 84.0


def test_phase_38_smoothquant_calibrate(client):
    """
    4. Test SOSS Phase 38 SmoothQuant scale migration.
    """
    res = client.post("/api/quantization/smoothquant/calibrate", json={
        "alpha": 0.5,
        "activation_max": 10.0,
        "weight_max": 2.5
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["computed_migration_scale"] > 0.0


def test_phase_39_lut_compile(client):
    """
    5. Test SOSS Phase 39 LUT bins compiler mapping.
    """
    res = client.post("/api/quantization/lut/compile", json={
        "bits": 3
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["look_up_table_bins"] == 8


def test_phase_37_weight_prune(client):
    """
    6. Test SOSS Phase 37 weight pruning simulation.
    """
    res = client.post("/api/quantization/weight/prune", json={
        "threshold": 0.2,
        "layer_weights": [0.1, 0.5, -0.05, 0.8]
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["computed_sparsity"] == 0.5


def test_phase_36_activation_mse(client):
    """
    7. Test SOSS Phase 36 activation MSE solver.
    """
    res = client.post("/api/quantization/activation/mse", json={
        "activations": [1.0, 2.0, 3.0],
        "bits": 4
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert "mean_squared_error" in data


def test_phase_35_qat_distill(client):
    """
    8. Test SOSS Phase 35 student-teacher gap trace.
    """
    res = client.post("/api/quantization/qat/distill", json={
        "student_loss": 0.4,
        "teacher_loss": 0.1
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["distillation_gap"] == 0.3
    assert data["status_evaluation"] == "DISVERGING"


def test_phase_34_spinquant_rotate(client):
    """
    9. Test SOSS Phase 34 learned SpinQuant rotations.
    """
    res = client.post("/api/quantization/spinquant/rotate", json={
        "vector": [10.0, -10.0]
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["max_value_before"] == 10.0
    assert data["max_value_after"] < 10.0


def test_phase_32_ternary_entropy_optimize(client):
    """
    10. Test SOSS Phase 32 ternary entropy maximization.
    """
    res = client.post("/api/quantization/ternary-entropy/optimize", json={
        "distribution": [0.333, 0.333, 0.334]
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert data["computed_entropy_bits"] > 1.5
