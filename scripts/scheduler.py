import os
import sys

def run_scheduler():
    # Environment gate to prevent accidental runs
    if os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER") != "1":
        print("Loki scheduler is disabled by default. Set SOLOMON_ENABLE_LOKI_SCHEDULER=1 to run.")
        return

    print("Running Loki scheduler...")
    # Scheduler logic would go here

if __name__ == "__main__":
    run_scheduler()
