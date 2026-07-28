from flask import Blueprint, jsonify, request
from .laboratory.hypothesis_manager import HypothesisCard
from .invention.problem_registry import ProblemRecord
from .invention.invention_manager import InventionManager
import uuid

oswald_bp = Blueprint('oswald', __name__, url_prefix='/api/oswald')

# In-memory stubs for the MVP API
_problems = []
_inventions = []

@oswald_bp.route('/invention/problems', methods=['GET', 'POST'])
def problems():
    if request.method == 'POST':
        data = request.json or {}
        prob = ProblemRecord(
            problem_id=str(uuid.uuid4()),
            title=data.get('title', 'Unknown Problem'),
            description=data.get('description', ''),
            domain=data.get('domain', 'General'),
            source=data.get('source', 'Manual')
        )
        _problems.append(prob)
        return jsonify({"status": "success", "problem_id": prob.problem_id})
    return jsonify({"status": "success", "problems": [p.__dict__ for p in _problems]})

@oswald_bp.route('/invention/generate', methods=['POST'])
def generate_invention():
    data = request.json or {}
    problem_id = data.get('problem_id')
    problem = next((p for p in _problems if p.problem_id == problem_id), None)
    if not problem:
        return jsonify({"status": "error", "message": "Problem not found"}), 404

    manager = InventionManager()
    inv = manager.generate_candidate(problem, ["System Optimization", "Data Structures"])
    _inventions.append(inv)
    return jsonify({"status": "success", "invention_id": inv.invention_id, "summary": inv.summary})

@oswald_bp.route('/invention/candidates', methods=['GET'])
def get_candidates():
    return jsonify({"status": "success", "candidates": [i.__dict__ for i in _inventions]})
