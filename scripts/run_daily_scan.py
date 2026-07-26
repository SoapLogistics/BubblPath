import os
import sys

# Required to load the modules from the root path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.solomon_futures_engine import FuturesEngine

def inject_context_pack(content):
    """
    Injects output into the daily codex context pack.
    """
    codex_path = "docs/solomon_daily_codex_context.md"
    try:
        with open(codex_path, "a") as f:
            f.write(f"\n\n## Futures Daily Scan Output\n```json\n{content}\n```\n")
    except Exception as e:
        print(f"Failed to inject context pack: {e}")

def run_scan(seed=None, deterministic=False, mode="default"):
    if mode == "futures":
        print("Running futures scan...")
        engine = FuturesEngine()

        # Simulate ingest & assessment
        targets = [
            {"id": "match_001", "confidence": 91.5},
            {"id": "match_002", "confidence": 80.1},
            {"id": "match_003", "confidence": 75.0}
        ]

        projections = []
        for t in targets:
            proj = engine.generate_projection(t["id"], t["confidence"], {"type": "daily_scan"})
            projections.append(proj)

        import json
        output = json.dumps(projections, indent=2)
        inject_context_pack(output)

        print("Futures output generated and injected into context pack.")
        return {"status": "success", "mode": "futures", "projections": projections}

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
    run_scan(mode=mode)
