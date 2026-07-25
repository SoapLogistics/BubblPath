import os
import openai
import hashlib
import tiktoken
import orjson
from flask import Flask, request, jsonify, Response
from flask_compress import Compress
from flask_caching import Cache
from solomon_efficiency_toolkit import SolomonEfficiencyToolkit
from solomon_extreme_efficiency_toolkit import SolomonExtremeEfficiencyToolkit
from solomon_invention_land import SolomonInventionEngine

app = Flask(__name__)

# Initialize the Unified Invention Engine
# Handles Memory Pooling, Radix Drafting, KAN Splines, and Annealing Stateful Logic
INVENTION_ENGINE = SolomonInventionEngine()

# Enforce strict 1MB limit on request payloads to prevent OOM
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Enable Gzip compression to save bandwidth on API responses
compress = Compress()
compress.init_app(app)

# Setup simple in-memory caching for repeated requests
cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
cache.init_app(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    # Apply real efficiency toolkit optimizations to the payload
    # 1. Strip naive HTML
    user_message = SolomonExtremeEfficiencyToolkit.strip_html_tags(user_message)
    # 2. Minify whitespace
    user_message = SolomonEfficiencyToolkit.remove_duplicate_whitespace(user_message)
    # 3. Fast Sliding Window string truncation before tokenization
    user_message = SolomonExtremeEfficiencyToolkit.sliding_window_truncate(user_message, 8000)

    # 4. Enforce strict token limits to save OpenAI costs and latency
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(user_message)
    if len(tokens) > 2000:
        # Truncate strictly to 2000 tokens
        user_message = enc.decode(tokens[:2000])

    # 5. String Interning for duplicate memory pointers
    user_message = SolomonExtremeEfficiencyToolkit.intern_string(user_message)

    # Route request payload into Paged Ring Memory Pool for zero-GC allocation
    raw_payload = request.get_data()
    if raw_payload:
        INVENTION_ENGINE.ingest_http_request(raw_payload)

    # Master prompt lifecycle: Anneal Workers, MoE Routing, Speculative Drafting
    draft_reply, cache_route = INVENTION_ENGINE.process_prompt(user_message)

    if draft_reply:
        payload = orjson.dumps({"reply": f"Draft: {draft_reply}", "cached": True, "source": "ngram_drafting"})
        return Response(payload, mimetype='application/json')

    # Always compute cache_key since it's used to store the final OpenAI response
    cache_key = f"chat_{hashlib.sha256(user_message.encode('utf-8')).hexdigest()}"

    if cache_route == "hash":
        # Try checking Hash Cache for identical prompts
        cached_response = cache.get(cache_key)
        if cached_response:
            payload = orjson.dumps({"reply": cached_response, "cached": True, "source": "hash_cache"})
            return Response(payload, mimetype='application/json')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    reply = response.choices[0].message["content"]

    # Store in cache regardless of route to build future history
    cache.set(cache_key, reply)

    # Provide feedback to the unified engine to train Radix/N-Grams and shift memory topology
    INVENTION_ENGINE.register_success(user_message, reply)

    payload = orjson.dumps({"reply": reply, "source": "openai"})
    return Response(payload, mimetype='application/json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
