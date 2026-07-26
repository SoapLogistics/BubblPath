from flask import Blueprint, jsonify
from core.swarm.resident_framework import global_checkpointer, global_messaging

resident_blueprint = Blueprint("residents", __name__)

route_key = "resident_dashboard"
readiness_key = "resident_api_active"

@resident_blueprint.route("/api/residents/status", methods=["GET"])
def get_residents_status():
    """Returns the current state and health of all Residents from the zero-copy memory map."""
    checkpoints = global_checkpointer.read_all()
    return jsonify({
        "status": "success",
        "residents": checkpoints
    })

@resident_blueprint.route("/api/residents/messages", methods=["GET"])
def get_residents_messages():
    """Returns the most recent structured events published by the Residents."""
    messages = global_messaging.get_messages(limit=50)
    return jsonify({
        "status": "success",
        "messages": messages
    })
