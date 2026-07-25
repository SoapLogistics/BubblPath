from flask import Blueprint, jsonify, request

memory_bp = Blueprint('memory', __name__, url_prefix='/api/v2/memory')

@memory_bp.route('/remember', methods=['POST'])
def remember_context():
    """Stores a System of Knowledge (SOK) card."""
    data = request.json
    return jsonify({"status": "success", "card_id": "temp_id_123"}), 201
