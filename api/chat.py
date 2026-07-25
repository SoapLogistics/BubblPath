import os
import logging
from typing import Dict, Any, Tuple
import openai
from flask import Blueprint, request, jsonify, Response
from werkzeug.exceptions import RequestEntityTooLarge

# Setup logger for API/Chat module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

chat_bp = Blueprint("chat_bp", __name__)

# Import the globally initialized limiter instance from app.py
from app import limiter

@chat_bp.route("/chat", methods=["POST"])
@limiter.limit("60 per minute") # Apply a safe and robust rate limit: 60 requests per minute
def chat() -> Tuple[Response, int]:
    """
    Harden chat endpoint with validation, logging, error handling, and structured response.
    """
    # 1. Validate JSON header and body presence
    if not request.is_json:
        logger.warning("Invalid request: Content-Type is not application/json")
        return jsonify({"error": "Content-Type must be application/json"}), 400

    try:
        data: Dict[str, Any] = request.get_json() or {}
    except RequestEntityTooLarge as e:
        # Re-raise Werkzeug's RequestEntityTooLarge so Flask's 413 global error handler captures it
        raise e
    except Exception as e:
        logger.error(f"Failed to parse JSON body: {e}")
        return jsonify({"error": "Malformed JSON payload"}), 400

    # 2. Extract and validate user message
    user_message: str = data.get("message", "")
    if not isinstance(user_message, str):
        logger.warning("Invalid request: 'message' parameter must be a string")
        return jsonify({"error": "'message' parameter must be a string"}), 400

    user_message = user_message.strip()
    if not user_message:
        logger.warning("Invalid request: Empty 'message' parameter")
        return jsonify({"error": "'message' parameter cannot be empty"}), 400

    logger.info("Forwarding chat request to OpenAI ChatCompletion API")

    # 3. Call OpenAI with safety measures: timeouts, explicit exceptions
    try:
        # Retrieve API key inside route dynamically or fallback to current config
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("Configuration error: OPENAI_API_KEY environment variable is missing")
            return jsonify({"error": "Internal server configuration error"}), 500

        openai.api_key = api_key

        # Set request timeout to prevent hanging requests using request_timeout (for old openai SDK)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            request_timeout=30.0  # 30-second timeout
        )

        reply: str = response.choices[0].message["content"]
        logger.info("Successfully received reply from OpenAI API")
        return jsonify({"reply": reply}), 200

    except openai.error.Timeout as e:
        logger.error(f"OpenAI API call timed out: {e}")
        return jsonify({"error": "Request to OpenAI timed out. Please try again."}), 504
    except openai.error.AuthenticationError as e:
        logger.error(f"OpenAI API Authentication failed: {e}")
        return jsonify({"error": "Upstream authentication failed"}), 502
    except openai.error.RateLimitError as e:
        logger.error(f"OpenAI API rate limit exceeded: {e}")
        return jsonify({"error": "Upstream rate limit exceeded. Please try again later."}), 429
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API returned an error: {e}")
        return jsonify({"error": "An upstream AI service error occurred"}), 502
    except Exception as e:
        logger.error(f"Unexpected error encountered during OpenAI call: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@chat_bp.errorhandler(400)
def bad_request(error: Any) -> Tuple[Response, int]:
    return jsonify({"error": "Bad Request", "message": str(error)}), 400

@chat_bp.errorhandler(404)
def not_found(error: Any) -> Tuple[Response, int]:
    return jsonify({"error": "Not Found", "message": str(error)}), 404

@chat_bp.errorhandler(500)
def internal_error(error: Any) -> Tuple[Response, int]:
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500
