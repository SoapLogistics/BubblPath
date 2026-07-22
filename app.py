import os
import time
import logging
from flask import Flask, request, jsonify
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

# Configure structured logging for production observation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("JulesApp")

app = Flask(__name__)

# Track application start time for uptime calculations
START_TIME = time.time()

# Read custom LLM API configuration or default to Standard OpenAI
api_key = os.environ.get("OPENAI_API_KEY", "placeholder_key")
api_base = os.environ.get("SOLOMON_LLM_API_BASE") or os.environ.get("OPENAI_API_BASE")

# Instantiate OpenAI client with modern client interface
# We supply custom timeouts to avoid hanging connections in production
try:
    if api_base:
        logger.info(f"Initializing modern OpenAI client with custom base URL: {api_base}")
        openai_client = OpenAI(api_key=api_key, base_url=api_base, timeout=30.0)
    else:
        logger.info("Initializing modern OpenAI client with default base URL")
        openai_client = OpenAI(api_key=api_key, timeout=30.0)
except Exception as e:
    logger.critical(f"Failed to initialize OpenAI client: {str(e)}")
    openai_client = None

# Infused Combined Persona: OpenAI Codex & Google Jules Systems Architect
# This directive ensures strict formatting with a large, bold, and colored "RECOMMENDED NEXT STEP" section.
SYSTEM_INSTRUCTIONS = (
    "You are the unified intelligence of OpenAI Codex and Google Jules (Google's Principal Systems Architect). "
    "You are an extremely elite, pragmatic software engineer who focuses on ultra-clean, highly performant, secure, "
    "and robust system foundations. Provide elegant code, diagnose architecture gaps with absolute precision, "
    "and always maintain elite systems standards.\n\n"
    "CRITICAL FORMATTING INSTRUCTION:\n"
    "At the very end of your response, you MUST append a highly visible, large, bold, and colored "
    "\"RECOMMENDED NEXT STEP\" section. "
    "For example, use Markdown format like this:\n"
    "### **<span style='color:#ff0055;'>RECOMMENDED NEXT STEP</span>**\n"
    "[Specify the exact subsequent action, such as code implementation, deployment, or validation here]\n"
    "Make sure you never omit this section. It is a strict system-level requirement."
)

def get_memory_footprint():
    """Parses system information to estimate memory footprint (RSS) in MB."""
    try:
        # On Linux systems, we can parse /proc/self/status for accurate RSS
        if os.path.exists("/proc/self/status"):
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            return f"{float(parts[1]) / 1024:.2f} MB"

        # Fallback to standard library resource module if available
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        # On macOS, maxrss is in bytes; on Linux, it's in kilobytes
        if os.uname().sysname == "Darwin":
            return f"{usage.ru_maxrss / (1024 * 1024):.2f} MB"
        else:
            return f"{usage.ru_maxrss / 1024:.2f} MB"
    except Exception as e:
        logger.warning(f"Could not retrieve memory telemetry: {str(e)}")
        return "N/A"

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles conversational interactions.
    Validates JSON payload, queries OpenAI via modern client interface,
    applies systems architecture system-level instructions, and handles robust error scenarios.
    """
    if not request.is_json:
        logger.error("Request payload is not JSON")
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        logger.error("Received empty JSON payload")
        return jsonify({"error": "Empty or invalid JSON payload"}), 400

    user_message = data.get("message")
    if user_message is None or str(user_message).strip() == "":
        logger.error("Missing or empty 'message' key in request payload")
        return jsonify({"error": "Missing or empty 'message' parameter"}), 400

    if not openai_client:
        logger.critical("OpenAI client was not initialized properly")
        return jsonify({"error": "OpenAI client is not configured on this server"}), 500

    model = os.environ.get("SOLOMON_MODEL", "gpt-3.5-turbo")
    logger.info(f"Processing chat request with model={model}")

    try:
        # Modern non-deprecated OpenAI chat completion call
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except RateLimitError as e:
        logger.error(f"OpenAI Rate Limit reached: {str(e)}")
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    except APIConnectionError as e:
        logger.error(f"OpenAI Connection failure: {str(e)}")
        return jsonify({"error": "Failed to connect to the model provider. Check network or base URL."}), 503
    except APIError as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return jsonify({"error": f"Model provider API error: {e.message}"}), 502
    except Exception as e:
        logger.exception("An unexpected error occurred during LLM inference")
        return jsonify({"error": f"An unexpected system error occurred: {str(e)}"}), 500

@app.route("/health", methods=["GET"])
def health():
    """
    Production-grade system health and telemetry monitoring probe.
    Reports uptime, memory footprint, client health, and basic configurations.
    """
    uptime = time.time() - START_TIME
    memory_rss = get_memory_footprint()

    # Assess OpenAI client connectivity configuration status
    client_status = "unconfigured"
    if openai_client:
        client_status = "ready"
        if not api_key or api_key == "placeholder_key":
            client_status = "ready_fallback_mode"

    status_data = {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "memory_footprint": memory_rss,
        "openai_client_state": client_status,
        "api_base": api_base or "default-openai",
        "timestamp": time.time()
    }
    logger.info("Health telemetry checked successfully")
    return jsonify(status_data), 200

if __name__ == "__main__":
    # Standard production binding, fallback to 10000 per requirements
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
