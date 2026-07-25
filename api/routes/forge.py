from flask import Blueprint, jsonify, request
from solomon_forge.scaffolder import InMemoryAppScaffolder

forge_bp = Blueprint('forge', __name__, url_prefix='/api/v2/forge')

@forge_bp.route('/scaffold', methods=['POST'])
def generate_scaffold():
    """Zero-IO application generation."""
    data = request.json or {}
    project_name = data.get("name", "untitled_project")

    result = InMemoryAppScaffolder.generate_flask_scaffold(project_name)

    return jsonify({"status": "success", "data": result}), 201
