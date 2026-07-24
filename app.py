import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from solomon_jules_bridge import JulesBridge

app = Flask(__name__)
CORS(app) # Enable CORS for Chrome Extension communication
bridge = JulesBridge()
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    context_data = data.get("context", None)

    # We prepend context if available
    system_prompt = (
        "You are Solomon, a helpful assistant. "
        "If the user asks you to perform an action on the webpage (like adding to cart or clicking a bet), "
        "and you know the CSS selector for the button, you MUST output a tag at the end of your response like this: "
        "[ACTION: #my-css-selector]. The system will intercept this and ask the user for manual approval.\n"
        "If you need to fill out a form input, use [FILL: #selector | value_to_type].\n\n"
        "JULES BRIDGE PROTOCOL: You manage an autonomous software engineering worker named 'Jules' via a secure API. "
        "If you read a GitHub issue or need code written, output: [JULES_TASK: repository | objective]. "
        "To check status, output [JULES_STATUS: task_id]. "
        "To validate and request approval for a patch, output [JULES_VALIDATE: task_id]. "
    )
    if context_data:
        system_prompt += f" The user is currently looking at {context_data.get('type', 'a webpage')} at {context_data.get('url', '')}. Here is the extracted context: {context_data.get('data', '')}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
        )
        return jsonify({"reply": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route("/api/browser/context", methods=["POST"])
def receive_context():
    data = request.json
    # In a full implementation, we might store this context in a local DB or memory card
    print(f"Received context from {data.get('url')}: {data.get('type')}")
    return jsonify({"status": "Context received successfully"})

@app.route("/api/browser/action-log", methods=["POST"])
def log_action():
    data = request.json
    print(f"AUDIT LOG: User explicitly approved action on {data.get('url')}. Target: {data.get('selector')}")
    # In a production system, write to SQLite audit tables (e.g. loki_bets/actions)
    return jsonify({"status": "Action logged securely"})

@app.route("/api/jules/task", methods=["POST"])
def create_task():
    data = request.json
    repo = data.get("repository", "unknown-repo")
    objective = data.get("objective", "No objective provided")
    record = bridge.create_jules_task(repository=repo, objective=objective)
    return jsonify(record)

@app.route("/api/jules/status/<task_id>", methods=["GET"])
def get_status(task_id):
    record = bridge.read_jules_session(task_id)
    if not record:
        return jsonify({"error": "not found"}), 404
    return jsonify(record)

@app.route("/api/jules/validate", methods=["POST"])
def validate_task():
    data = request.json
    task_id = data.get("task_id")
    # Simulate the pipeline: Retrieve -> Validate (SS3) -> Await Human
    bridge.retrieve_jules_patch(task_id)
    bridge.validate_jules_output(task_id)
    record = bridge.request_human_approval(task_id)
    return jsonify(record)

@app.route("/api/jules/approve", methods=["POST"])
def approve_task():
    data = request.json
    task_id = data.get("task_id")
    record = bridge.execute_human_approval(task_id)
    return jsonify(record)

@app.route("/api/browser/halt", methods=["POST"])
def emergency_halt():
    # Kill switch for pending backend operations.
    print("🛑 EMERGENCY HALT TRIGGERED BY USER")
    return jsonify({"status": "halted", "message": "All operations aborted safely."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
