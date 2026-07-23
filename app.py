import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI, OpenAIError

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chatgpt-flask-app")

app = Flask(__name__)

# Initialize modern, thread-safe OpenAI client
# Uses environment variables: OPENAI_API_KEY, and optional OPENAI_BASE_URL
# Includes robust default timeout configuration
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key if api_key else "dummy-key-for-local-fallback",
    timeout=30.0,
)

# Use gpt-4o-mini as a robust and efficient default, allowing override
DEFAULT_MODEL = "gpt-4o-mini"
MODEL_NAME = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)

@app.route("/chat", methods=["POST"])
def chat():
    # 1. Validation of request payload existence
    if not request.is_json:
        logger.warning("Incoming request is not JSON or lacks content-type application/json.")
        return jsonify({"error": "Content-Type must be application/json"}), 400

    try:
        data = request.get_json(silent=True)
    except Exception as e:
        logger.warning(f"Failed to parse JSON body: {str(e)}")
        return jsonify({"error": "Invalid or malformed JSON payload"}), 400

    if data is None:
        logger.warning("Request body parsed to None.")
        return jsonify({"error": "Missing JSON payload"}), 400

    # 2. Key validation and type checks
    if "message" not in data:
        logger.warning("Required 'message' field is missing from JSON payload.")
        return jsonify({"error": "Missing 'message' field in payload"}), 400

    user_message = data.get("message")
    if not isinstance(user_message, str):
        logger.warning(f"Invalid type for 'message' field: expected str, got {type(user_message).__name__}.")
        return jsonify({"error": "'message' field must be a string"}), 400

    # 3. Handle empty / blank messages safely
    user_message_stripped = user_message.strip()
    if not user_message_stripped:
        logger.warning("Empty or whitespace-only user message received.")
        return jsonify({"error": "'message' cannot be empty or whitespace-only"}), 400

    logger.info(f"Processing chat request with model {MODEL_NAME}...")

    # 4. Resilient OpenAI integration
    try:
        # Modern v1.0.0+ client syntax
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": user_message_stripped}],
        )
        reply = response.choices[0].message.content
        logger.info("Successfully generated reply from OpenAI.")
        return jsonify({"reply": reply})

    except OpenAIError as oe:
        # Catch all standard OpenAI API issues (RateLimitError, AuthenticationError, Timeout, etc.)
        logger.error(f"OpenAI Client Error: {str(oe)}", exc_info=True)
        return jsonify({
            "error": "Failed to communicate with OpenAI service. Please try again later.",
            "details": str(oe)
        }), 502

    except Exception as e:
        # Unexpected internal error fallback
        logger.error(f"Internal unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An unexpected error occurred internally. Please try again later."
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
