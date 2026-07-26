import os
import sys

def main():
    enable_scheduler = os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER", "false")
    if enable_scheduler.lower() == "true":
        print("Running daily scan via scheduler...")
    else:
        print("Scheduler disabled. Exiting.")

if __name__ == "__main__":
    main()
