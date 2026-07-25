import os
import logging
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from api.routes.cognitive import cognitive_bp
from api.routes.memory import memory_bp
from api.routes.chat import chat_bp
from api.routes.finance import finance_bp
from api.routes.forge import forge_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Security & Configuration
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB strict payload limit

    # Initialize Rate Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Register Domain Blueprints
    app.register_blueprint(cognitive_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(forge_bp)

    @app.route("/health", methods=["GET"])
    def root_health():
        return jsonify({"status": "healthy", "service": "solomon-gateway"}), 200

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Resource not found."), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error="Method not allowed."), 405

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
