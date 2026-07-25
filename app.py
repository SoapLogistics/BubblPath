import os
import openai
from flask import Flask, request, jsonify, render_template
from solomon_quantized_memory import QuantizedBrainMap
from solomon_joe_bridge import JoeOmegaEngine

app = Flask(__name__)
unified_memory = QuantizedBrainMap()
joe_daemon = JoeOmegaEngine()
unified_memory.start_ans() # Start background autonomic nervous system
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/api/memory/ingest", methods=["POST"])
def ingest_memory():
    data = request.json
    if not data or "content" not in data or "type" not in data:
        return jsonify({"error": "Missing 'content' or 'type'"}), 400

    node_id = unified_memory.ingest(
        node_type=data["type"],
        content=data["content"],
        importance=data.get("importance", 0.5),
        valence=data.get("valence", 0.0),
        arousal=data.get("arousal", 0.0)
    )
    return jsonify({"status": "success", "node_id": node_id})

@app.route("/api/memory/recall", methods=["GET", "POST"])
def recall_memory():
    if request.method == "POST":
        data = request.json or {}
        query = data.get("query", "")
        top_k = data.get("top_k", 5)
    else:
        query = request.args.get("query", "")
        top_k_str = request.args.get("top_k", "5")
        top_k = int(top_k_str) if top_k_str.isdigit() else 5

    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    results = unified_memory.recall(query, top_k=top_k)
    return jsonify({"status": "success", "results": results})

@app.route("/api/memory/consolidate", methods=["POST"])
def consolidate_memory():
    unified_memory.consolidate()
    stats = unified_memory.get_stats()
    return jsonify({"status": "success", "stats": stats})

@app.route("/api/memory/blob", methods=["GET"])
def get_memory_blob():
    """Zero-copy binary response for UI God Eye visualizer"""
    if os.path.exists("solomon_brain_map.bin"):
        with open("solomon_brain_map.bin", "rb") as f:
            data = f.read()
        return data, 200, {'Content-Type': 'application/octet-stream'}
    return jsonify({"status": "empty"}), 404

@app.route("/api/memory/dream", methods=["POST"])
def dream_memory():
    data = request.json or {}
    steps = data.get("steps", 10)
    unified_memory.dream_cycle(max_steps=steps)
    stats = unified_memory.get_stats()
    return jsonify({"status": "success", "message": "Dream cycle complete.", "stats": stats})

@app.route("/api/joe/queue-blueprint", methods=["POST"])
def joe_queue():
    data = request.json or {}
    blueprint_name = data.get("name", "Unnamed Blueprint")
    blueprint_text = data.get("blueprint", "")

    if not blueprint_text:
        return jsonify({"error": "Missing 'blueprint' text"}), 400

    try:
        joe_daemon.queue_blueprint(blueprint_name, blueprint_text)
        return jsonify({"status": "success", "message": "Blueprint added to J.O.E. Queue."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/joe/status", methods=["GET"])
def joe_status():
    return jsonify(joe_daemon.get_status())

@app.route("/joe", methods=["GET"])
def joe_chat_ui():
    return render_template("joe_chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
