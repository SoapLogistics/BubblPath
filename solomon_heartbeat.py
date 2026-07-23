import time
import requests
import os

API_URL = os.environ.get("SOLOMON_API_URL", "http://localhost:10000")

def trigger_heartbeat():
    try:
        response = requests.post(f"{API_URL}/heartbeat", json={"trigger": "scheduler"})
        print(f"Heartbeat trigger status: {response.status_code}")
    except Exception as e:
        print(f"Failed to trigger heartbeat: {e}")

if __name__ == "__main__":
    while True:
        trigger_heartbeat()
        time.sleep(60)
