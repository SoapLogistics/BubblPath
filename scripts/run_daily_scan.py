import os

def run_scan():
    seed = os.environ.get("LOKI_SCAN_SEED")
    if seed:
        print(f"Running deterministic scan with seed {seed}")
    else:
        print("Running normal scan")

if __name__ == "__main__":
    run_scan()
