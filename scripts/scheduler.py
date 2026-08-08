import logging
import os
import subprocess
import sys

logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)


def run_scheduler():
    if os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER") != "1":
        logger.info("Loki scheduler is disabled by default. Set SOLOMON_ENABLE_LOKI_SCHEDULER=1 to run.")
        return

    if os.environ.get("SOLOMON_RUN_FUTURES_SCAN") == "1":
        script_path = os.path.join(os.path.dirname(__file__), "run_daily_scan.py")
        subprocess.run([sys.executable, script_path, "--mode=SHADOW"], check=True)

if __name__ == "__main__":
    run_scheduler()
