import os
import sys
import time

def run_loki_scheduler():
    if not os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER"):
        print("Loki scheduler is gated by SOLOMON_ENABLE_LOKI_SCHEDULER. Exiting.")
        return

    # In test mode, we do not run an immediate scan unless requested.
    # Otherwise, avoid running scheduled scans during tests unless explicitly enabled.
    is_test = os.environ.get("TESTING") == "1"
    run_initial = os.environ.get("SOLOMON_RUN_INITIAL_LOKI_SCAN") == "1"

    if is_test and not run_initial:
        print("Test mode enabled without SOLOMON_RUN_INITIAL_LOKI_SCAN. Loki scheduler skipping initial scan.")
    else:
        print("Loki scheduler running scan...")
        # Simulate Loki fetching only needed feeds with TTL cache
        # Fallback samples with reason when live data fails

    print("Loki scheduler finished cycle.")

if __name__ == "__main__":
    run_loki_scheduler()
