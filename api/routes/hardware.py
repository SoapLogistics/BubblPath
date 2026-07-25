from flask import Blueprint, jsonify, request
from solomon_hardware.quantization.sparsity import SparsityEngine

hardware_bp = Blueprint('hardware', __name__, url_prefix='/api/v2/hardware')

@hardware_bp.route('/optimize/sparsity', methods=['POST'])
def apply_sparsity():
    """Applies 2:4 NM Sparsity to a dense weight matrix payload."""
    data = request.json or {}
    weights = data.get("weights", [])

    if not weights:
        return jsonify({"error": "No weights provided."}), 400

    try:
        result = SparsityEngine.optimize_payload(weights)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
