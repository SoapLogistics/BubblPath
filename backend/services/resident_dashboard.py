from core.solomon_resident_framework import ResidentFramework
from flask import Blueprint, jsonify

# Resident dashboard HTTP facade
resident_dashboard_bp = Blueprint('resident_dashboard', __name__)

route_key = "/api/residents/dashboard"
readiness_key = "resident_dashboard_ready"

_framework_instance = None

def get_framework():
    global _framework_instance
    if _framework_instance is None:
        # Singleton access to the zero-copy mmap framework
        _framework_instance = ResidentFramework()
    return _framework_instance

@resident_dashboard_bp.route("/api/residents/dashboard", methods=["GET"])
def get_dashboard():
    """
    Exposes resident health, state, and tasks through a safe HTTP facade
    reading from the zero-copy memory.
    """
    try:
        framework = get_framework()
        states = framework.get_all_states()

        results = []
        for state in states:
            results.append({
                "name": state.name,
                "last_heartbeat": state.last_heartbeat,
                "state_code": state.state_code,
                "task_id": state.task_id,
                "last_checkpoint": state.last_checkpoint
            })

        return jsonify({
            "status": "success",
            "residents": results
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve resident dashboard: {str(e)}"
        }), 500
