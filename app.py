import os
import logging
from typing import Optional, Dict, Any
from flask import Flask, jsonify, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure root/application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Limiter globally
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://"
)

def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Application factory pattern to construct the Flask application.
    Enforces security hardening, rate-limiting, and modular Blueprint routes.
    """
    app = Flask(__name__)

    # Default production-hardened configurations
    # Limit max request body content size to 1MB to prevent DoS attacks
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

    # Apply configuration overrides (especially useful for testing)
    if config_override:
        app.config.update(config_override)

    # 1. Apply ProxyFix middleware to trust upstream reverse proxy headers (e.g. Render, Cloudflare)
    # Secures remote IP detection for Flask-Limiter and audit logs
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1) # type: ignore

    # 2. Bind and initialize Flask-Limiter
    limiter.init_app(app)

    # 3. Register Blueprints
    from api.chat import chat_bp
    app.register_blueprint(chat_bp)

    # Apply global rate limits if needed, or blueprint-specific rate-limits (configured next)

    # 4. Global generic fallback error handlers
    @app.errorhandler(413)
    def payload_too_large(error: Any) -> tuple[Response, int]:
        logger.warning("Request blocked: Payload exceeded MAX_CONTENT_LENGTH limit of 1MB")
        return jsonify({"error": "Payload Too Large", "message": "Request body size exceeds the limit of 1MB"}), 413

    @app.errorhandler(500)
    def internal_error(error: Any) -> tuple[Response, int]:
        logger.error(f"Global internal server error captured: {error}")
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred on the server"}), 500

    logger.info("Flask Application Factory successfully initialized")
    return app

if __name__ == "__main__":
    # Standard fallback path for local direct execution
    app = create_app()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
