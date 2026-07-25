from flask import Blueprint, jsonify, request

cognitive_bp = Blueprint('cognitive', __name__, url_prefix='/api/v2/cognitive-core')

@cognitive_bp.route('/health', methods=['GET'])
def health_check():
    """Liveness probe for the Cognitive Core."""
    return jsonify({"status": "active", "module": "GabrielRouter"}), 200

@cognitive_bp.route('/run-loop', methods=['POST'])
def run_loop():
    """Triggers a cycle of the Perpetual Learning Engine."""
    # TODO: Route via Event Bus or execute Gabriel Task
    return jsonify({"status": "success", "message": "SPLE cycle initiated."}), 202
