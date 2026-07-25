import os
import openai
import hashlib
from flask import Flask, request, jsonify
from flask_compress import Compress
from flask_caching import Cache

app = Flask(__name__)
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

    # Try checking cache first for identical prompts
    cache_key = f"chat_{hashlib.sha256(user_message.encode('utf-8')).hexdigest()}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return jsonify({"reply": cached_response, "cached": True})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    reply = response.choices[0].message["content"]

    # Store in cache
    cache.set(cache_key, reply)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
