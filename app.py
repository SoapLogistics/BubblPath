import os
from typing import Tuple, Any

from flask import Flask, request, jsonify, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from openai import OpenAI

app = Flask(__name__)

# Security: Tell Flask it is behind a proxy (like Render). This ensures `get_remote_address`
# gets the real user IP, rather than the internal load balancer IP, preventing global rate limits.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)  # type: ignore

# Security: Limit payloads to 1MB to prevent DoS attacks
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Security: Rate limit endpoints to prevent abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Instantiate the global client. If OPENAI_API_KEY is not set, we pass a dummy value
# to prevent the app from crashing on startup (which breaks the /health endpoint).
# The client will fail gracefully when attempting an actual API call.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy_key"))


@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat() -> Tuple[Response, int]:
    """Handles chat interactions with the OpenAI API."""
    data = request.json or {}
    if "message" not in data:
        return jsonify({"error": "Missing 'message'"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": str(data["message"])}],
        )
        # Type ignored below due to dynamic properties on the response object
        return jsonify({"reply": response.choices[0].message.content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
@limiter.exempt
def health() -> Tuple[Response, int]:
    """Health check endpoint for load balancers."""
    return jsonify({"status": "healthy"}), 200


@app.errorhandler(413)
def request_entity_too_large(error: Any) -> Tuple[Response, int]:
    """Custom handler for large payloads."""
    return jsonify({"error": "Payload too large. Maximum size is 1MB."}), 413


@app.errorhandler(429)
def ratelimit_handler(error: Any) -> Tuple[Response, int]:
    """Custom handler for rate limit violations."""
    return jsonify({"error": "Rate limit exceeded"}), 429


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
