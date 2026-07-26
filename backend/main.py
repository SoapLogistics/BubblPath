import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, request
from services.solomon_joe_bridge import JoeOmegaEngine

app = Flask(__name__)
joe_engine = JoeOmegaEngine()

@app.route('/api/joe/status', methods=['GET'])
def joe_status():
    return jsonify(joe_engine.get_status())

@app.route('/api/joe/queue-blueprint', methods=['POST'])
def joe_queue_blueprint():
    data = request.json or {}
    blueprint = data.get("blueprint", "empty")
    approved = data.get("approved", False)
    return jsonify(joe_engine.queue_blueprint(blueprint, approved=approved))

if __name__ == "__main__":
    enable_scheduler = os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER", "false")
    if enable_scheduler.lower() == "true":
        print("Loki scheduler started.")
    app.run(port=8000)
