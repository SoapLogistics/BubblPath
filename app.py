import os
import openai
from flask import Flask, request, jsonify
from solomon_core.soss.synthesizer import CleanRoomSynthesizer
import types

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# A dummy target function that SOSS will hot-reload dynamically
def dynamic_capability_slot(*args, **kwargs):
    return "Not yet synthesized."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

@app.route("/api/soss/synthesize", methods=["POST"])
def soss_synthesize():
    data = request.json
    algorithm_request = data.get("algorithm_request")

    if not algorithm_request:
        return jsonify({"error": "algorithm_request is required"}), 400

    synthesizer = CleanRoomSynthesizer()

    # We pass our dummy function to be hot-reloaded
    result = synthesizer.synthesize_and_inject(algorithm_request, dynamic_capability_slot)

    if result["status"] == "success":
        # Let's test the hot-reloaded function!
        # (Assuming the request didn't require complex args for this demo,
        # or we just return the success message)
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route("/api/soss/invoke_dynamic", methods=["POST"])
def soss_invoke():
    """Endpoint to actually run the dynamically injected function."""
    data = request.json or {}
    args = data.get("args", [])
    kwargs = data.get("kwargs", {})

    try:
        # Calls whatever logic has been hot-reloaded into this slot
        result = dynamic_capability_slot(*args, **kwargs)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
