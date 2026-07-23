import os
import time
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
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

# Track startup time for health checks
START_TIME = time.time()

# Read API Key with a warning if missing
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY environment variable is not set. API calls will fail.")
else:
    logger.info("OPENAI_API_KEY is configured.")

# Initialize the modern thread-safe OpenAI client
# We pass an explicit empty string/dummy key if none exists to avoid immediate client validation crashes
client = OpenAI(api_key=api_key or "sk-dummy-key-configured-for-startup")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Harden, streamline, and validate the chat endpoint with robust error handling
    and payload validation.
    """
    # 1. Validate request payload is JSON
    data = request.get_json(silent=True)
    if data is None:
        logger.warning("Received invalid or non-JSON request body.")
        return jsonify({"error": "Malformed request. Payload must be valid JSON."}), 400

    # 2. Validate 'message' field is present and is a non-empty string
    user_message = data.get("message")
    if not user_message or not isinstance(user_message, str) or not user_message.strip():
        logger.warning(f"Payload validation failed. message: {user_message}")
        return jsonify({"error": "Invalid payload. 'message' must be a non-empty string."}), 400

    user_message = user_message.strip()

    # 3. Check if OpenAI API key is missing
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("Attempted chat completion but OPENAI_API_KEY is not set.")
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

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except APITimeoutError as e:
        logger.error(f"OpenAI API request timed out: {str(e)}")
        return jsonify({"error": "OpenAI API request timed out. Please try again."}), 504

    except RateLimitError as e:
        logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
        return jsonify({"error": "OpenAI API rate limit exceeded. Please try again later."}), 429

    except AuthenticationError as e:
        logger.error(f"OpenAI authentication failed: {str(e)}")
        return jsonify({
            "error": "OpenAI authentication failed. Please check the API key configuration."
        }), 500

    except APIConnectionError as e:
        logger.error(f"Failed to connect to OpenAI API: {str(e)}")
        return jsonify({"error": "Failed to connect to OpenAI API."}), 502

    except APIError as e:
        logger.error(f"OpenAI API error occurred: {str(e)}")
        return jsonify({"error": f"OpenAI API error: {e.message}"}), 502

    except Exception as e:
        logger.critical(f"Unexpected system exception during chat completion: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/health", methods=["GET"])
def health():
    """
    Production-grade monitoring health check endpoint that returns active system metrics.
    """
    uptime = time.time() - START_TIME
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))

    status_info = {
        "status": "healthy" if has_api_key else "degraded",
        "uptime_seconds": round(uptime, 2),
        "openai_configured": has_api_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "chatgpt-flask-app",
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
