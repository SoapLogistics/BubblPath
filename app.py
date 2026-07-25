import os
import openai
from flask import Flask, request, jsonify
import numpy as np
from solomon_hardware.zero_copy_memory import ZeroCopyMemorySubstrate

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize the Zero-Copy Memory Substrate globally
memory_substrate = ZeroCopyMemorySubstrate("gabriel_knowledge_base.bin", max_records=100000)

@app.route("/api/memory/zero-copy", methods=["POST"])
def add_zero_copy_memory():
    data = request.json
    try:
        record_id = data.get("id", 0)
        valence = data.get("valence", 0.0)
        arousal = data.get("arousal", 0.0)
        concept_hash = data.get("concept_hash", 0)

        # If no embedding provided, generate a random one for demonstration
        embedding_data = data.get("embedding")
        if embedding_data:
            embedding = np.array(embedding_data, dtype=np.float32)
        else:
            embedding = np.random.rand(128).astype(np.float32)

        idx = memory_substrate.add_record(record_id, valence, arousal, concept_hash, embedding)

        return jsonify({"status": "success", "index": idx, "message": "Zero-copy memory stored instantly."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/memory/zero-copy/search", methods=["POST"])
def search_zero_copy_memory():
    data = request.json
    try:
        embedding_data = data.get("embedding")
        if not embedding_data:
            # Generate random query for demonstration if none provided
            query_embedding = np.random.rand(128).astype(np.float32)
        else:
            query_embedding = np.array(embedding_data, dtype=np.float32)

        top_k = data.get("top_k", 5)

        results = memory_substrate.search_similar(query_embedding, top_k=top_k)

        # Format results (numpy arrays are not json serializable directly)
        formatted_results = []
        for res in results:
            formatted_results.append({
                "index": res["index"],
                "similarity": res["similarity"],
                "record": {
                    "id": res["record"]["id"],
                    "timestamp": res["record"]["timestamp"],
                    "valence": res["record"]["valence"],
                    "arousal": res["record"]["arousal"],
                    "concept_hash": res["record"]["concept_hash"]
                    # Omitting the raw embedding in response to save bandwidth
                }
            })

        return jsonify({"status": "success", "results": formatted_results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

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
