import pytest
from solomon_quantization_50_step_optimizers import QuantizationFiftyStepOptimizers

def test_run_all_50_steps():
    result = QuantizationFiftyStepOptimizers.run_all_50_steps()
    assert result["status"] == "success"
    assert result["steps_executed"] == 50
    assert len(result["logs"]) == 50
    assert "Step 1: " in result["logs"][0]
    assert "Step 50: " in result["logs"][49]

import json
from app import app

def test_api_execute_quantization_50_step_optimize():
    with app.test_client() as client:
        response = client.post("/api/command-center/quantization/50-step-optimize")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["steps_executed"] == 50
        assert len(data["logs"]) == 50
