import os
import logging
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI, RateLimitError, APIConnectionError, APIStatusError

# Configure structured, professional logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s in %(module)s: %(message)s",
)
logger = logging.getLogger("chatgpt-flask-app")

app = Flask(__name__)

# Enforce a 1 MB payload size limit to prevent Denial of Service (DOS) attacks
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

# Set up IP-based rate limiting to prevent endpoint abuse
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per day", "30 per minute"],
    storage_uri="memory://",
)

# Initialize the modernized OpenAI client
# It automatically retrieves OPENAI_API_KEY from the environment
client = OpenAI()


@app.after_request
def add_security_headers(response):
    """Adds essential security headers to mitigate common web vulnerabilities."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none';"
    )
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


@app.errorhandler(400)
def bad_request_handler(e):
    """Custom handler for Bad Request errors (including malformed JSON)."""
    logger.warning(f"Bad Request: {e}")
    return (
        jsonify(
            {
                "error": "Bad Request",
                "message": getattr(
                    e, "description", "Malformed or invalid request payload."
                ),
            }
        ),
        400,
    )


@app.errorhandler(404)
def not_found_handler(e):
    """Custom handler for Not Found errors."""
    return (
        jsonify(
            {
                "error": "Not Found",
                "message": "The requested resource was not found on this server.",
            }
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed_handler(e):
    """Custom handler for Method Not Allowed errors."""
    return (
        jsonify(
            {
                "error": "Method Not Allowed",
                "message": "The method is not allowed for the requested URL.",
            }
        ),
        405,
    )


@app.errorhandler(429)
def ratelimit_handler(e):
    """Custom handler for Rate Limit Exceeded errors."""
    logger.warning(f"Rate limit exceeded by IP: {request.remote_addr}")
    return (
        jsonify(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
            }
        ),
        429,
    )


@app.route("/health", methods=["GET"])
@limiter.exempt  # Exempt health checks from rate limiting to facilitate steady uptime probing
def health():
    """Health check endpoint to monitor application and environment readiness."""
    api_key_configured = bool(os.environ.get("OPENAI_API_KEY"))
    status_code = 200 if api_key_configured else 503
    status_str = "healthy" if api_key_configured else "unhealthy"

    response_payload = {
        "status": status_str,
        "environment": {"openai_api_key_configured": api_key_configured},
    }

    if not api_key_configured:
        logger.error(
            "Health check failed: OPENAI_API_KEY environment variable is not configured."
        )
        response_payload["message"] = (
            "Service misconfigured: OpenAI API key is missing."
        )
    else:
        logger.info("Health check passed.")

    return jsonify(response_payload), status_code


@app.route("/chat", methods=["POST"])
def chat():
    """
    Main endpoint for OpenAI Chat Completions.
    Enforces size limits, validates payload structure, and handles API exceptions gracefully.
    """
    logger.info(f"Incoming /chat request from IP: {request.remote_addr}")

    # Check if request has JSON payload
    if not request.is_json:
        logger.warning("Rejected non-JSON request payload.")
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Content-Type must be application/json.",
                }
            ),
            400,
        )

    data = request.get_json()
    if data is None:
        logger.warning("Rejected empty or malformed JSON payload.")
        return jsonify({"error": "Bad Request", "message": "Invalid JSON body."}), 400

    user_message = data.get("message")

    # Input validation: check presence
    if user_message is None:
        logger.warning("Rejected request lacking the 'message' field.")
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Missing required field: 'message'.",
                }
            ),
            400,
        )

    # Input validation: coerce/check type
    if not isinstance(user_message, str):
        logger.warning("Rejected non-string 'message' payload.")
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "The 'message' field must be a string.",
                }
            ),
            400,
        )

    # Input validation: length limits (prevent token inflation attacks)
    user_message = user_message.strip()
    if not user_message:
        logger.warning("Rejected empty message payload.")
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "The 'message' field cannot be empty or whitespace only.",
                }
            ),
            400,
        )

    if len(user_message) > 4000:
        logger.warning(
            f"Rejected message exceeding maximum length: {len(user_message)} characters."
        )
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "The message exceeds the maximum allowed length of 4000 characters.",
                }
            ),
            400,
        )

    try:
        logger.info(f"Sending message to OpenAI (length: {len(user_message)})...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1000,  # Cap response token length to keep costs predictable
        )

        reply = response.choices[0].message.content
        logger.info("Successfully received reply from OpenAI.")
        return jsonify({"reply": reply})

    except RateLimitError as e:
        logger.error(f"OpenAI RateLimitError encountered: {e}")
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "OpenAI API rate limit exceeded. Please try again shortly.",
                }
            ),
            429,
        )

    except APIConnectionError as e:
        logger.error(f"OpenAI APIConnectionError encountered: {e}")
        return (
            jsonify(
                {
                    "error": "Service Unavailable",
                    "message": "Could not connect to OpenAI API servers. Please check network connectivity.",
                }
            ),
            503,
        )

    except APIStatusError as e:
        logger.error(
            f"OpenAI APIStatusError encountered: status_code={e.status_code}, response={e.response}"
        )
        return (
            jsonify(
                {
                    "error": f"OpenAI API Error ({e.status_code})",
                    "message": "OpenAI returned an error. Please try again later.",
                }
            ),
            e.status_code,
        )

    except Exception as e:
        logger.critical(f"Unexpected internal system error: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please contact the administrator.",
                }
            ),
            500,
        )


if __name__ == "__main__":
    # Ensure port is dynamic/configurable
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
