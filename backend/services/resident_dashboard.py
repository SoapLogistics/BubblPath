import json
from flask import Blueprint, jsonify

readiness_key = "resident_dashboard_facade"

dashboard_bp = Blueprint("resident_dashboard", __name__)

# To be set externally by app.py
lifecycle_engine = None

@dashboard_bp.route("/api/residents/status", methods=["GET"])
def get_status():
    if not lifecycle_engine:
        return jsonify({"status": "error", "message": "Lifecycle Engine not initialized"}), 500

    status_data = []
    for res in lifecycle_engine.registration.get_all():
        status_data.append(res.get_health_status())

    issues = lifecycle_engine.watchdog.check_health()
    events = [
        {"sender": e.sender, "type": e.event_type, "payload": e.payload, "timestamp": e.timestamp}
        for e in lifecycle_engine.messaging.get_events(limit=50)
    ]

    return jsonify({
        "status": "success",
        "residents": status_data,
        "watchdog_issues": issues,
        "recent_events": events
    })
