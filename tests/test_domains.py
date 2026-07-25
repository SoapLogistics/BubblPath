import pytest
from api.app import create_app
from solomon_finance.quant_models import LokiQuantEngine

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_loki_black_scholes_math():
    # ATM call option value should be positive
    price = LokiQuantEngine.black_scholes_call(100.0, 100.0, 1.0, 0.05, 0.2)
    assert price > 0.0
    assert round(price, 2) == 10.45

def test_loki_pricing_endpoint(client):
    response = client.post("/api/v2/finance/options/price", json={
        "S": 100.0, "K": 100.0, "T": 1.0, "r": 0.05, "sigma": 0.2
    })
    assert response.status_code == 200
    assert response.get_json()["price"] == 10.4506

def test_hephaestus_scaffold_endpoint(client):
    response = client.post("/api/v2/forge/scaffold", json={"name": "test_app"})
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["architecture"] == "Flask Monolith"
    assert "test_app" in data["vfs"]
    assert data["metrics"]["disk_io_operations"] == 0
