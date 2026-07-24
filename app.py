import os
import time
import logging
from datetime import datetime, timezone
import threading
from flask import Flask, request, jsonify
import httpx
import openai
from openai import (
    OpenAI,
    APIError,
    RateLimitError,
    APITimeoutError,
    AuthenticationError,
    APIConnectionError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
)
logger = logging.getLogger("chatgpt-flask-app")

app = Flask(__name__)

# 1. Protect against DoS by limiting request payload sizes to 1MB
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

# Track startup time for health checks
START_TIME = time.time()

# Thread-safe metrics collection
metrics_lock = threading.Lock()
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_latency": 0.0,
}

# Read API Key with a warning if missing
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY environment variable is not set. API calls will fail.")
else:
    logger.info("OPENAI_API_KEY is configured.")

# 2. Configure a custom high-performance httpx.Client to prevent socket exhaustion
limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
http_client = httpx.Client(limits=limits, timeout=30.0)

# Initialize the modern thread-safe OpenAI client
client = OpenAI(
    api_key=api_key or "sk-dummy-key-configured-for-startup",
    http_client=http_client
)


@app.after_request
def add_security_headers(response):
    """
    3. Inject essential secure HTTP response headers to harden the browser security posture.
    """
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.route("/chat", methods=["POST"])
def chat():
    """
    Harden, streamline, and validate the chat endpoint with robust error handling,
    payload validation, and live metrics tracking.
    """
    with metrics_lock:
        metrics["total_requests"] += 1

    # 1. Validate request payload is JSON
    data = request.get_json(silent=True)
    if data is None:
        logger.warning("Received invalid or non-JSON request body.")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({"error": "Malformed request. Payload must be valid JSON."}), 400

    # 2. Validate 'message' field is present and is a non-empty string
    user_message = data.get("message")
    if not user_message or not isinstance(user_message, str) or not user_message.strip():
        logger.warning(f"Payload validation failed. message: {user_message}")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({"error": "Invalid payload. 'message' must be a non-empty string."}), 400

    user_message = user_message.strip()

    # 3. Check if OpenAI API key is missing
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("Attempted chat completion but OPENAI_API_KEY is not set.")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({
            "error": "Service configuration error. OpenAI API Key is missing on the server."
        }), 500

    logger.info(f"Processing chat request. Input length: {len(user_message)} characters.")

    try:
        # Call OpenAI Chat Completion API with the modern client interface
        start_api_time = time.time()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            timeout=30.0,  # 30-second timeout configuration for robustness
        )
        latency = time.time() - start_api_time
        logger.info(f"OpenAI API request completed successfully in {latency:.3f} seconds.")

        with metrics_lock:
            metrics["successful_requests"] += 1
            metrics["total_latency"] += latency

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except APITimeoutError as e:
        logger.error(f"OpenAI API request timed out: {str(e)}")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({"error": "OpenAI API request timed out. Please try again."}), 504

    except RateLimitError as e:
        logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({"error": "OpenAI API rate limit exceeded. Please try again later."}), 429

    except AuthenticationError as e:
        logger.error(f"OpenAI authentication failed: {str(e)}")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({
            "error": "OpenAI authentication failed. Please check the API key configuration."
        }), 500

    except APIConnectionError as e:
        logger.error(f"Failed to connect to OpenAI API: {str(e)}")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({"error": "Failed to connect to OpenAI API."}), 502

    except APIError as e:
        logger.error(f"OpenAI API error occurred: {str(e)}")
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({"error": f"OpenAI API error: {e.message}"}), 502

    except Exception as e:
        logger.critical(f"Unexpected system exception during chat completion: {str(e)}", exc_info=True)
        with metrics_lock:
            metrics["failed_requests"] += 1
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/health", methods=["GET"])
def health():
    """
    Production-grade monitoring health check endpoint that returns active system metrics.
    """
    uptime = time.time() - START_TIME
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))

    with metrics_lock:
        req_count = metrics["total_requests"]
        success_count = metrics["successful_requests"]
        fail_count = metrics["failed_requests"]
        tot_latency = metrics["total_latency"]

    avg_latency = (tot_latency / success_count) if success_count > 0 else 0.0

    status_info = {
        "status": "healthy" if has_api_key else "degraded",
        "uptime_seconds": round(uptime, 2),
        "openai_configured": has_api_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "chatgpt-flask-app",
        "metrics": {
            "total_requests": req_count,
            "successful_requests": success_count,
            "failed_requests": fail_count,
            "avg_latency_seconds": round(avg_latency, 4),
        }
    }

    # Return 200 even if degraded so we don't restart the container immediately,
    # but indicate the degraded state to orchestrators.
    return jsonify(status_info), 200


if __name__ == "__main__":
    # Allow configuring host and port via environment variables with safe, standard defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 10000))

    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port)
