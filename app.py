import os
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

from solomon_browser_companion import BrowserCompanionBackend

companion_backend = BrowserCompanionBackend()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

@app.route("/api/browser-companion/chat", methods=["POST"])
def browser_companion_chat():
    """
    Endpoint dedicated to the Browser Companion.
    Accepts context from the current tab and routes to the LLM backend
    which extracts proposed DOM actions.
    """
    auth = request.headers.get("Authorization")
    expected_auth = f"Bearer {os.environ.get('SOLOMON_INTERNAL_AUTH_KEY', '')}"

    if not os.environ.get('SOLOMON_INTERNAL_AUTH_KEY') or auth != expected_auth:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    message = data.get("message", "")
    context = data.get("context", {})

    result = companion_backend.process_chat(message, context, openai)
    return jsonify(result)

@app.route("/api/mnemosyne/remember", methods=["POST"])
def passive_learning_remember():
    """
    Stub endpoint for Passive Learning (Memory).
    The browser extension pings this every 45s of active viewing.
    """
    auth = request.headers.get("Authorization")
    expected_auth = f"Bearer {os.environ.get('SOLOMON_INTERNAL_AUTH_KEY', '')}"

    if not os.environ.get('SOLOMON_INTERNAL_AUTH_KEY') or auth != expected_auth:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    # Memory ingestion logic would go here.
    # Currently acting as a successful stub for the extension integration.
    return jsonify({"status": "memorized", "source": data.get("source")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
