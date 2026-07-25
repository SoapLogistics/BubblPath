import os
import time
import openai
from flask import Flask, request, jsonify
from solomon_learning_engine import gabriel_learner
from solomon_metrics import metrics_tracker

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    start_time = time.time()
    data = request.json
    user_message = data.get("message", "")

    # Prepend context from memory
    context = gabriel_learner.retrieve_context(user_message)
    augmented_message = context + user_message

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": augmented_message}],
        )
        reply = response.choices[0].message["content"]

        # Post-task Learning Loop
        gabriel_learner.extract_pattern(user_message, reply)
        gabriel_learner.compress_knowledge()

        latency = (time.time() - start_time) * 1000
        metrics_tracker.record_task(latency, success=True)

        return jsonify({"reply": reply})
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        metrics_tracker.record_task(latency, success=False)
        gabriel_learner.record_failure(user_message, str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/metrics", methods=["GET"])
def get_metrics():
    return jsonify(metrics_tracker.get_stats())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
