import time
import requests
import os

API_URL = os.environ.get("SOLOMON_API_URL", "http://localhost:10000")
API_TOKEN = os.environ.get("SOLOMON_API_TOKEN", "solomon-dev-token-99")

def trigger_heartbeat():
    try:
        response = requests.post(
            f"{API_URL}/heartbeat",
            json={"trigger": "scheduler"},
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        if response.status_code == 503:
            print("System is PAUSED_BLOCKED. Heartbeat pausing operations.")
        else:
            print(f"Heartbeat trigger status: {response.status_code}")
    except Exception as e:
        print(f"Failed to trigger heartbeat: {e}")

def trigger_reflection():
    try:
        response = requests.post(
            f"{API_URL}/system/reflect",
            json={"trigger": "nightly_reflection"},
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        print(f"Reflection trigger status: {response.status_code}")
    except Exception as e:
        print(f"Failed to trigger reflection: {e}")

if __name__ == "__main__":
    counter = 0
    while True:
        trigger_heartbeat()
        counter += 1

        # Trigger reflection roughly once an hour (every 60 heartbeats)
        if counter >= 60:
            trigger_reflection()
            counter = 0

        time.sleep(60)
