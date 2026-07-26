import os
import time

def run_scheduler():
    if not os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER"):
        print("Scheduler disabled.")
        return

    if os.environ.get("TESTING") and not os.environ.get("SOLOMON_RUN_INITIAL_LOKI_SCAN"):
        print("Scheduler skipping immediate scan in tests.")
        return

    log_dir = "local_log"
    os.makedirs(log_dir, exist_ok=True)
    # write to a controlled location instead of stdout
    with open(f"{log_dir}/scheduler_status.log", "a") as f:
        f.write(f"Scheduler ran at {time.time()}\n")

if __name__ == "__main__":
    run_scheduler()
