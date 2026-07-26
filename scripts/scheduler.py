import os
def run_scheduler():
    if os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER") == "true":
        print("Running daily scan")
if __name__ == "__main__":
    run_scheduler()
