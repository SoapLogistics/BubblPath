import os
import sys
import subprocess

def run_scheduler():
    # Environment gate to prevent accidental runs
    if os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER") != "1":
        print("Loki scheduler is disabled by default. Set SOLOMON_ENABLE_LOKI_SCHEDULER=1 to run.")
        return

    print("Running Loki scheduler...")

    # Run the daily futures scan if enabled
    if os.environ.get("SOLOMON_RUN_FUTURES_SCAN") == "1":
        print("Executing scheduled futures scan...")
        script_path = os.path.join(os.path.dirname(__file__), "run_daily_scan.py")
        subprocess.run([sys.executable, script_path, "--mode=futures"])

if __name__ == "__main__":
    run_scheduler()
