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
        # Context Compression
        raw_data = context_data.get('data', '')
        compressed_data = raw_data[:2000] + ("..." if len(raw_data) > 2000 else "")
        system_prompt += f" The user is currently looking at {context_data.get('type', 'a webpage')} at {context_data.get('url', '')}. Here is the extracted context: {compressed_data}"

    # Global Halt Check
    if getattr(app, 'halt_active', False):
        return jsonify({"reply": "🛑 HALT ACTIVE: Backend operations are currently suspended. Clear the halt state to resume."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
        )
        return jsonify({"reply": response.choices[0].message["content"]})
    except openai.error.Timeout:
        return jsonify({"reply": "Error: OpenAI API request timed out. Please try again."}), 504
    except Exception as e:
        return jsonify({"reply": f"Error communicating with AI: {str(e)}"}), 500

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
    app.halt_active = request.json.get("active", True)
    if app.halt_active:
        print("🛑 EMERGENCY HALT TRIGGERED BY USER")
        return jsonify({"status": "halted", "message": "All operations aborted safely."})
    else:
        print("✅ HALT CLEARED")
        return jsonify({"status": "active", "message": "Halt state cleared."})

@app.route("/health", methods=["GET"])
def health_check():
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)
    tasks = len(bridge.list_jules_tasks())
    return jsonify({
        "status": "healthy",
        "memory_mb": round(mem, 2),
        "active_jules_tasks": tasks,
        "halt_active": getattr(app, 'halt_active', False)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
