import os
import sys

def run_scan(seed=None, deterministic=False, mode="default"):
    if mode == "futures":
        # Integrating futures scan
        from services.futures.threshold_logic import evaluate_threshold, calculate_confidence

        # Determine 80/90 targets clearly classified
        targets = [
            {"name": "Target A", "confidence_val": 85.0},
            {"name": "Target B", "confidence_val": 92.0},
            {"name": "Target C", "confidence_val": 75.0}
        ]

        output_board = []
        for t in targets:
            conf = calculate_confidence(t["confidence_val"])
            if evaluate_threshold(conf, 90.0):
                threshold_class = "90"
            elif evaluate_threshold(conf, 80.0):
                threshold_class = "80"
            else:
                threshold_class = "none"

            output_board.append({
                "target": t["name"],
                "confidence": conf,
                "threshold_class": threshold_class,
                "status": "CLASSIFIED"
            })

        print("Futures output board generated deterministically.")
        return {"status": "success", "deterministic": True, "board": output_board}

    if deterministic and seed is not None:
        print(f"Running deterministic scan with seed {seed}")
        return {"status": "success", "deterministic": True, "seed": seed}

    print("Running random scan")
    return {"status": "success", "deterministic": False}

if __name__ == "__main__":
    mode = "default"
    for arg in sys.argv:
        if arg.startswith("--mode="):
            mode = arg.split("=")[1]

    # Gated by Loki scheduler flag
    if os.environ.get("SOLOMON_ENABLE_LOKI_SCHEDULER") == "1":
        run_scan(mode=mode)
    else:
        print("Loki scheduler is disabled by default. Set SOLOMON_ENABLE_LOKI_SCHEDULER=1 to run.")
