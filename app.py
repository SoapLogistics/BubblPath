import os
import openai
from flask import Flask, request, jsonify
from solomon_quantization_optimization import QuantizationOptimizer
from solomon_50_step_optimizers import FiftyStepQuantizationOptimizer

app = Flask(__name__)
quant_optimizer = QuantizationOptimizer()
fifty_step_optimizer = FiftyStepQuantizationOptimizer()
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

@app.route("/api/quantization/benchmarking", methods=["POST"])
def api_quant_benchmarking():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.unified_benchmarking(data.get("model_id", "default"), data.get("precision", "INT8"), data.get("seq_len", 1024)))

@app.route("/api/quantization/precision-ladder", methods=["POST"])
def api_quant_precision_ladder():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.precision_ladder(data.get("workload_type", "general")))

@app.route("/api/quantization/fleet-router", methods=["POST"])
def api_quant_fleet_router():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.fleet_router(data.get("hardware_target", "NVIDIA_GPU")))

@app.route("/api/quantization/outlier-control", methods=["POST"])
def api_quant_outlier_control():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.outlier_control(data.get("activation_tensor", [])))

@app.route("/api/quantization/multilingual-eval", methods=["POST"])
def api_quant_multilingual_eval():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.multilingual_evaluation(data.get("languages", ["en"])))

@app.route("/api/quantization/calibration-version", methods=["POST"])
def api_quant_calibration_version():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.calibration_versioning(data.get("dataset_id", "ds_1"), data.get("model_config", {})))

@app.route("/api/quantization/security-review", methods=["POST"])
def api_quant_security_review():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.artifact_security_review(data.get("artifact_path", "/model/weights.bin"), data.get("expected_hash", "")))

@app.route("/api/quantization/mixed-precision-search", methods=["POST"])
def api_quant_mixed_precision_search():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.mixed_precision_search(data.get("layers", 10), data.get("latency_budget_ms", 10.0)))

@app.route("/api/quantization/qat-recovery", methods=["POST"])
def api_quant_qat_recovery():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.selective_qat_recovery(data.get("sensitivities", {}), data.get("threshold", 0.8)))

@app.route("/api/quantization/sparse", methods=["POST"])
def api_quant_sparse():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(quant_optimizer.sparse_quantization(data.get("model_id", "default"), data.get("density", 0.5)))

@app.route("/api/quantization/50-step-optimize", methods=["POST"])
def api_quant_50_step_optimize():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    return jsonify(fifty_step_optimizer.optimize_all(data.get("model_id", "default_model")))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
