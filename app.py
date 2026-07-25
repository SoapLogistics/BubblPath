import os
import json
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, g
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI
from solomon_core.event_bus import CognitiveEventBus
from solomon_core.sple.scheduler import SystemScheduler
from solomon_core.sple.prometheus import PrometheusEngine
from solomon_core.gabriel.router import GabrielTaskRouter

# Initialize core services
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app() -> Flask:
    """
    Application Factory for Solomon OS API Gateway.
    Optimized for a 20-year lifespan: strict typing, payload limits, rate limiting, and exact IP resolution.
    """
    app = Flask(__name__)

    # --- Configuration ---
    # Enforce a 1MB max payload to prevent DoS via large JSON bodies.
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
    app.config["JSON_SORT_KEYS"] = False

    # Enable correct IP resolution behind reverse proxies (e.g., Render)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Initialize extensions
    limiter.init_app(app)

    # Validate essential environment variables early
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # In a real environment we might fail fast.
        # For development/testing we allow it to start, but the client will fail on use.
        print("WARNING: OPENAI_API_KEY not set.")

    auth_key = os.environ.get("SOLOMON_INTERNAL_AUTH_KEY", "dev_default_key")
    app.config["AUTH_KEY"] = auth_key

    # Initialize OpenAI v1.x client (fallback to a dummy key to allow the app to boot without it)
    openai_client = OpenAI(api_key=api_key if api_key else "dummy_key_to_allow_boot")
    app.extensions['openai'] = openai_client

    # Initialize OS v2.0 Subsystems
    bus = CognitiveEventBus()
    scheduler = SystemScheduler(bus)
    prometheus = PrometheusEngine(bus)
    gabriel = GabrielTaskRouter(api_key)

    app.extensions['bus'] = bus
    app.extensions['scheduler'] = scheduler
    app.extensions['gabriel'] = gabriel

    # Start background loops
    scheduler.start()

    # --- Middleware ---
    @app.before_request
    def enforce_json():
        if request.method in ["POST", "PUT", "PATCH"]:
            if not request.is_json:
                return jsonify({"error": "Unsupported Media Type. Content-Type must be application/json"}), 415

    @app.before_request
    def enforce_auth():
        # Exempt health checks from auth
        if request.path == "/health":
            return

        provided_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        if provided_key != app.config["AUTH_KEY"]:
            return jsonify({"error": "Unauthorized"}), 401

    # --- Routes ---
    @app.route("/health", methods=["GET"])
    @limiter.exempt
    def health_check():
        return jsonify({"status": "healthy", "version": "2.0.0"}), 200

    @app.route("/chat", methods=["POST"])
    @limiter.limit("10 per minute")
    def chat():
        data: Dict[str, Any] = request.get_json()
        user_message: str = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400

        try:
            # Route complex tasks to Gabriel Engine instead of raw OpenAI API
            if data.get("use_gabriel", False):
                gabriel: GabrielTaskRouter = app.extensions['gabriel']
                result = gabriel.execute_task(user_message, {"source": "chat_endpoint"})
                return jsonify({"reply": result["consensus"], "metadata": result}), 200
            else:
                client: OpenAI = app.extensions['openai']
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}],
                )
                reply = response.choices[0].message.content
                return jsonify({"reply": reply}), 200

        except Exception as e:
            # We log exceptions in a production system.
            print(f"Error during chat execution: {e}")
            bus: CognitiveEventBus = app.extensions['bus']
            bus.publish("metrics.friction", {"source": "/chat", "error": str(e)})
            return jsonify({"error": "Internal Server Error"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=10000)
