import os
from flask import Flask, request, jsonify
from openai import OpenAI, OpenAIError

app = Flask(__name__)

# Attempt to instantiate client if API key is provided, but allow app to load for health checks
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy_key"))
except OpenAIError:
    client = None

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"error": "OpenAI client is not initialized"}), 500

    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    user_message = data.get("message", "")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
