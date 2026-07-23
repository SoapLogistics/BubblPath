import os
from openai import OpenAI
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Initialize modern thread-safe OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def index():
    try:
        return render_template("solomon_loki_workspace.html")
    except Exception as e:
        return jsonify({"error": "UI template not found", "details": str(e)}), 404

@app.route("/chat", methods=["POST"])
def chat():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    user_message = data.get("message")

    if not user_message or not isinstance(user_message, str):
        return jsonify({"error": "Valid 'message' string is required"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/picks", methods=["GET"])
def get_picks():
    picks = [
        {"id": 1, "sport": "NBA", "match": "Lakers vs Warriors", "pick": "Lakers +3.5", "confidence": 0.85},
        {"id": 2, "sport": "NFL", "match": "Chiefs vs Ravens", "pick": "Over 52.5", "confidence": 0.78},
    ]
    return jsonify({"status": "success", "picks": picks})

@app.route("/api/command-center/kalshi/simulate", methods=["POST"])
def simulate_kalshi():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    market = data.get("market", "Unknown Market")
    wager = data.get("wager", 0)

    # Simulate processing the Kalshi prediction market bet
    result = {
        "status": "success",
        "message": f"Simulated bet of ${wager} on '{market}'.",
        "simulated_outcome": "pending",
        "expected_roi": 0.05
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
