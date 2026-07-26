import os
import sys
import argparse
from typing import Dict, Any, List

try:
    from core.futures.futures_engine import process_futures_data
except ImportError:
    # Just in case this gets run without the path set properly
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from core.futures.futures_engine import process_futures_data

def generate_mock_futures_data() -> List[Dict[str, Any]]:
    """Generates deterministic mock data for the futures scan."""
    return [
        {"id": "evt_01", "confidence": 85.5, "probability": 75.0, "performance_score": 60.0},
        {"id": "evt_02", "confidence": 92.0, "probability": 88.0, "performance_score": 91.0},
        {"id": "evt_03", "confidence": 40.0, "probability": 50.0, "performance_score": 45.0},
        {"id": "evt_04", "confidence": 79.9, "probability": 79.9, "performance_score": 79.9},
    ]

def inject_to_daily_codex(processed_data: List[Dict[str, Any]]):
    """Injects results into docs/solomon_daily_codex_context.md"""
    codex_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'solomon_daily_codex_context.md')
    if os.path.exists(codex_path):
        with open(codex_path, 'a') as f:
            f.write("\n\n## Futures Daily Scan Results\n")
            for item in processed_data:
                metrics = item["data_health"]["metrics"]
                f.write(f"- ID: {item['data_health']['id']}, "
                        f"80-Breach: {metrics['breached_80']}, "
                        f"90-Breach: {metrics['breached_90']}\n")

def run_scan(seed=None, deterministic=False, mode=None):
    if mode == "futures":
        # Check Loki Scheduler Environment Flag
        if os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER") != "1":
            print("Loki scheduler is disabled. Set SOLOMON_ENABLE_LOKI_SCHEDULER=1 to run.")
            return {"status": "error", "message": "Scheduler disabled"}

        print("Running futures scan...")
        raw_data = generate_mock_futures_data()
        processed_data = process_futures_data(raw_data)

        inject_to_daily_codex(processed_data)

        # Deterministic output for tests
        print(f"Processed {len(processed_data)} futures records.")
        for item in processed_data:
            metrics = item["data_health"]["metrics"]
            if metrics["breached_90"]:
                print(f"Target {item['data_health']['id']} classified: 90")
            elif metrics["breached_80"]:
                print(f"Target {item['data_health']['id']} classified: 80")
            else:
                print(f"Target {item['data_health']['id']} classified: NEUTRAL")

        return {"status": "success", "mode": "futures", "data": processed_data}

    if deterministic and seed is not None:
        print(f"Running deterministic scan with seed {seed}")
        return {"status": "success", "deterministic": True, "seed": seed}
    print("Running random scan")
    return {"status": "success", "deterministic": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default=None)
    args = parser.parse_args()

    run_scan(mode=args.mode)
