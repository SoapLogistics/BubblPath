import pytest
import numpy as np
from api.app import create_app
from solomon_hardware.quantization.sparsity import SparsityEngine

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_nm_sparsity_math():
    # 2x4 matrix
    dense_weights = np.array([
        [1.0, 0.5, 3.0, 0.2],
        [4.0, 1.0, 2.0, 5.0]
    ])
    sparse = SparsityEngine.apply_2_4_sparsity(dense_weights)

    # Check that exactly 2 elements per block (row) are zeroed
    assert np.count_nonzero(sparse[0]) == 2
    assert np.count_nonzero(sparse[1]) == 2

    # Check that the smallest absolute values were zeroed
    assert sparse[0][1] == 0.0 # 0.5 was zeroed
    assert sparse[0][3] == 0.0 # 0.2 was zeroed
    assert sparse[0][0] == 1.0 # 1.0 kept
    assert sparse[0][2] == 3.0 # 3.0 kept

def test_hardware_api_endpoint(client):
    payload = {
        "weights": [
            [0.1, 0.9, 0.2, 0.8],
            [0.9, 0.1, 0.8, 0.2]
        ]
    }
    response = client.post("/api/v2/hardware/optimize/sparsity", json=payload)
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["sparsity_achieved"] == 50.0
