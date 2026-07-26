"""
backend/main.py
Backend entrypoint for Solomon.
"""
import os
import json

def get_joe_status():
    from backend.services.solomon_joe_bridge import get_status
    return get_status()

def queue_joe_blueprint(packet):
    from services.solomon_joe_bridge import queue_blueprint
    return queue_blueprint(packet)

if __name__ == "__main__":
    if os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER") == "true":
        print("Loki Scheduler Started")
    print("Backend Ready")
