import os
import time
import openai
from flask import Flask, request, jsonify
from solomon_learning_engine import gabriel_learner
from solomon_metrics import metrics_tracker
from solomon_abstract_reasoning import abstraction_engine
from solomon_curiosity_director import curiosity_director
from solomon_gabriel_100_step_learning_optimizers import gabriel_100_step_optimizer

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

@app.route("/system/run-learning-cycle", methods=["POST"])
def run_learning_cycle():
    """
    Manually triggers the background learning loops:
    1. Compresses raw patterns into abstractions.
    2. Directs curiosity to generate research tasks.
    """
    compression_results = abstraction_engine.run_compression_cycle()
    curiosity_results = curiosity_director.scan_frontier()

    return jsonify({
        "compression_cycle": compression_results,
        "curiosity_cycle": curiosity_results
    })

@app.route("/system/gabriel/100-step-optimize", methods=["POST"])
def run_100_step_optimization():
    """
    Executes the 100-step Gabriel Engine optimization pipeline.
    This pushes the 'compounding learning' philosophy to its limits,
    optimizing everything from memory hygiene to curiosity routing.
    """
    result = gabriel_100_step_optimizer.run_100_step_pipeline()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
