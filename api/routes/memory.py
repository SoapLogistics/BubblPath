from flask import Blueprint, jsonify, request

memory_bp = Blueprint('memory', __name__, url_prefix='/api/v2/memory')

@memory_bp.route('/remember', methods=['POST'])
def remember_context():
    """Stores a System of Knowledge (SOK) card via Advanced Graph Engine."""
    from solomon_memory.graph.engine import MnemosyneGraphEngine

    data = request.json or {}
    content = data.get("content", "Empty Memory")
    cluster_id = data.get("cluster_id", 0)

    engine = MnemosyneGraphEngine()
    card_id = engine.store_card(content=content, cluster_id=cluster_id)

    return jsonify({"status": "success", "card_id": card_id}), 201

@memory_bp.route('/active-context/<int:cluster_id>', methods=['GET'])
def get_active_context(cluster_id):
    """Retrieves TTL-validated context for a specific cluster."""
    from solomon_memory.graph.engine import MnemosyneGraphEngine

    engine = MnemosyneGraphEngine()
    context = engine.retrieve_active_context(cluster_id=cluster_id)

    return jsonify({"status": "success", "data": context}), 200
