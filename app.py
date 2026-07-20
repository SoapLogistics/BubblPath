import os
import openai
from flask import Flask, request, jsonify

from gabriel_engine.core.perpetual_loop import GabrielPerpetualLoop

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Instantiate Gabriel's perpetual absorption loop engine
gabriel_loop = GabrielPerpetualLoop()


@app.route("/chat", methods=["POST"])
def chat():
    """
    Original Chat Completion endpoint.
    """
    data = request.json or {}
    user_message = data.get("message", "")

    # Check if we have an API key configured before making actual OpenAI call
    if not openai.api_key:
        return jsonify({
            "reply": f"Mock ChatGPT response: I received your message '{user_message}'. (OpenAI API key not set)"
        })

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
        )
        return jsonify({"reply": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"reply": f"Error communicating with OpenAI: {str(e)}"}), 500


@app.route("/api/gabriel/assimilate", methods=["POST"])
def assimilate():
    """
    Triggers Gabriel's multi-stage assimilation loop on a target project/source path.
    """
    data = request.json or {}
    project_name = data.get("project_name")
    source_location = data.get("source_location")

    if not project_name or not source_location:
        return jsonify({
            "status": "error",
            "message": "Both 'project_name' and 'source_location' parameters are required."
        }), 400

    source_type = data.get("source_type", "source_repository")
    aggressive_mode = data.get("aggressive_mode", True)  # Code Thief Mode enabled by default!
    decision_overrides = data.get("decision_overrides", {})

    try:
        result = gabriel_loop.assimilate_project(
            project_name=project_name,
            source_location=source_location,
            source_type=source_type,
            aggressive_mode=aggressive_mode,
            decision_overrides=decision_overrides
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"An error occurred during assimilation: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/gabriel/records", methods=["GET"])
def get_records():
    """
    Returns all generated AcquisitionRecords.
    """
    records_dict = {
        name: record.to_dict()
        for name, record in gabriel_loop.acquisition_records.items()
    }
    return jsonify(records_dict)


@app.route("/api/gabriel/anatomies", methods=["GET"])
def get_anatomies():
    """
    Returns all generated ProgramAnatomyCards.
    """
    anatomies_dict = {
        name: card.to_dict()
        for name, card in gabriel_loop.anatomy_cards.items()
    }
    return jsonify(anatomies_dict)


@app.route("/api/gabriel/capabilities", methods=["GET"])
def get_capabilities():
    """
    Returns all extracted CapabilityMemoryCards.
    """
    capabilities_dict = {
        name: [c.to_dict() for c in caps_list]
        for name, caps_list in gabriel_loop.capability_cards.items()
    }
    return jsonify(capabilities_dict)


@app.route("/api/gabriel/crucible", methods=["GET"])
def get_crucible_reports():
    """
    Returns all evaluation crucible reports.
    """
    reports_dict = {
        name: report.to_dict()
        for name, report in gabriel_loop.crucible_reports.items()
    }
    return jsonify(reports_dict)


@app.route("/api/gabriel/implementations", methods=["GET"])
def get_implementations():
    """
    Returns all generated clean-room code implementations.
    """
    return jsonify(gabriel_loop.native_implementations)


@app.route("/api/gabriel/status", methods=["GET"])
def get_status():
    """
    Returns high-level stats on historical assimilation cycles and loop status.
    """
    history = gabriel_loop.assimilation_history
    return jsonify({
        "status": "active",
        "total_assimilations": len(history),
        "history": history,
        "mode": "aggressive_code_thief_enabled"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
