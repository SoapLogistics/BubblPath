from flask import Blueprint, jsonify, request
from solomon_finance.quant_models import LokiQuantEngine
from solomon_finance.data_provider import LightweightMarketStream

finance_bp = Blueprint('finance', __name__, url_prefix='/api/v2/finance')

@finance_bp.route('/options/price', methods=['POST'])
def price_option():
    """Ultra-fast Black-Scholes pricing."""
    data = request.json or {}
    S = data.get("S", 100.0)
    K = data.get("K", 100.0)
    T = data.get("T", 1.0)
    r = data.get("r", 0.05)
    sigma = data.get("sigma", 0.2)

    # Leverages lru_cache under the hood for extreme efficiency
    price = LokiQuantEngine.black_scholes_call(S, K, T, r, sigma)

    return jsonify({"status": "success", "price": round(price, 4)}), 200

@finance_bp.route('/market/snapshot', methods=['GET'])
def market_snapshot():
    """Zero-IO synthetic market data fetch."""
    provider = LightweightMarketStream()
    data = provider.fetch_data({"asset": "BTC"})
    return jsonify({"status": "success", "data": data}), 200
