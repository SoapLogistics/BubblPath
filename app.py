import os
import openai
import time
from flask import Flask, request, jsonify
from solomon_metrics import SolomonMetricsEngine
from solomon_learning_engine import HolographicLearningCore

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize global engines
metrics_engine = SolomonMetricsEngine()
learning_core = HolographicLearningCore(metrics_engine)

@app.route("/chat", methods=["POST"])
def chat():
    start_time = time.time()
    data = request.json
    user_message = data.get("message", "")

    success = False
    valence = 0.5  # Neutral default
    arousal = 0.5

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
        )
        reply = response.choices[0].message["content"]
        success = True
        valence = 0.8  # Positive interaction
    except Exception as e:
        reply = f"Error: {str(e)}"
        valence = 0.1  # Negative outcome
        arousal = 0.9  # High urgency/error

    duration_ms = (time.time() - start_time) * 1000

    # Track every interaction via zero-copy mmap
    metrics_engine.record_interaction(
        duration_ms=duration_ms,
        success=success,
        valence=valence,
        arousal=arousal,
        endpoint="/chat",
        request_content=user_message
    )

    return jsonify({"reply": reply})

@app.route("/system/run-learning-cycle", methods=["POST"])
def run_learning_cycle():
    """Triggers the HolographicLearningCore retrocausal evaluation"""
    start_time = time.time()

    try:
        result = learning_core.execute_learning_cycle()
        success = True
        valence = 0.9
    except Exception as e:
        result = {"status": "error", "message": str(e)}
        success = False
        valence = 0.1

    duration_ms = (time.time() - start_time) * 1000

    # Also track the learning cycle itself as an experiment!
    metrics_engine.record_interaction(
        duration_ms=duration_ms,
        success=success,
        valence=valence,
        arousal=0.7,
        endpoint="/system/run-learning-cycle",
        request_content="run_cycle"
    )

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
