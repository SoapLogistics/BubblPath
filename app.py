import os
import openai
from flask import Flask, request, jsonify
from solomon_unified_memory import UnifiedMemoryGraph

app = Flask(__name__)
unified_memory = UnifiedMemoryGraph()
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/api/memory/ingest", methods=["POST"])
def ingest_memory():
    data = request.json
    if not data or "content" not in data or "type" not in data:
        return jsonify({"error": "Missing 'content' or 'type'"}), 400

    node_id = unified_memory.ingest(
        node_type=data["type"],
        content=data["content"],
        importance=data.get("importance", 0.5)
    )
    return jsonify({"status": "success", "node_id": node_id})

@app.route("/api/memory/recall", methods=["GET", "POST"])
def recall_memory():
    if request.method == "POST":
        data = request.json
        query = data.get("query", "")
        top_k = data.get("top_k", 5)
    else:
        query = request.args.get("query", "")
        top_k = int(request.args.get("top_k", 5))

    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    results = unified_memory.recall(query, top_k=top_k)
    return jsonify({"status": "success", "results": results})

@app.route("/api/memory/consolidate", methods=["POST"])
def consolidate_memory():
    unified_memory.consolidate()
    stats = unified_memory.get_stats()
    return jsonify({"status": "success", "stats": stats})

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
