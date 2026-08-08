import json
import logging
import os
import sys
import time
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.live_data_ingestion import OmniDataRouter
from services.solomon_futures_engine import Candidate, FuturesEngine, FuturesRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [FUTURES_SCAN] %(message)s")
logger = logging.getLogger("futures_scan")

def inject_daily_report(run_id, output_summary):
    codex_path = "docs/solomon_daily_codex_context.md"
    date_str = time.strftime("%Y-%m-%d")
    report = f"""
<!-- FUTURES_DAILY_START:{date_str}_{run_id} -->
### Futures Run {run_id}
```json
{json.dumps(output_summary, indent=2)}
```
<!-- FUTURES_DAILY_END:{date_str}_{run_id} -->
"""
    try:
        with open(codex_path, "a") as f:
            f.write(report)
    except Exception as e: # noqa: BLE001
        logger.error(f"Failed to append to context pack: {e}")

def run_scan(mode="TEST", seed=42):
    logger.info(f"Starting futures scan. Mode: {mode}")

    engine = FuturesEngine()
    repo = FuturesRepository()
    run_id = str(uuid.uuid4())

    # Hyper-Quantization: Generator Stream for candidates to keep RAM near 0
    def yield_candidates():
        router = OmniDataRouter()
        for candidate in router.stream_global_events():
            yield candidate

    stats = {"received": 0, "simulated": 0, "confirmed_90": 0, "skipped": 0}

    for raw in yield_candidates():
        stats["received"] += 1
        if repo.check_idempotency(raw["id"], mode):
            logger.info(f"Skipping {raw['id']} - already executed in {mode}")
            stats["skipped"] += 1
            continue

        c = Candidate(
            candidate_id=raw["id"], event_id=f"evt_{raw['id']}", domain=raw["domain"],
            source_name="global_omni_scan", source_record_id=f"rec_{raw['id']}",
            source_mode=mode, source_timestamp=str(time.time()), ingested_at=str(time.time()),
            pre_simulation_confidence=raw["conf"], data_quality_score=95.0,
            features={
                "base_prob": raw["base_prob"],
                "volatility_index": raw["volatility"],
                "historical_support": raw["support"],
                "geopolitical_risk": raw["geopolitical_risk"]
            }
        )

        res = engine.process_candidate(c, seed=seed)
        
        # Stream result straight to SQLite without holding it in a Python array
        repo.save_run(res)

        if res.status != "PRE_SIM_NOT_QUALIFIED":
            stats["simulated"] += 1
        if res.status == "CONFIRMED_90_PLUS":
            stats["confirmed_90"] += 1

        logger.info(f"Processed {raw['id']} -> {res.status}")
        
        # Trigger GC implicitly by not holding `res` reference
        del res
        del c

    summary = {"run_id": run_id, "mode": mode, "stats": stats}
    inject_daily_report(run_id, summary)

    # Use nonzero exit code if catastrophic failure occurred (skipped here for happy path simulation)
    return summary

if __name__ == "__main__":
    mode_arg = "TEST"
    for arg in sys.argv:
        if arg.startswith("--mode="):
            mode_arg = arg.split("=")[1]

    if mode_arg == "LIVE" and not os.environ.get("FUTURES_LIVE_AUTHORIZATION"):
        logger.error("LIVE mode requested without governance authorization.")
        sys.exit(1)

    run_scan(mode=mode_arg)
