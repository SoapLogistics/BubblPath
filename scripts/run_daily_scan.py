import os
import sys
import uuid
import time
import json
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.solomon_futures_engine import FuturesEngine, Candidate, FuturesRepository

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
    except Exception as e:
        logger.error(f"Failed to append to context pack: {e}")

def run_scan(mode="TEST", seed=42):
    logger.info(f"Starting futures scan. Mode: {mode}")

    engine = FuturesEngine()
    repo = FuturesRepository()
    run_id = str(uuid.uuid4())

    # Mocking real input retrieval for Loki scans
    raw_candidates = [
        {"id": "tgt_A", "event": "Lakers vs Celtics", "pick": "Lakers -5.5", "market": "DraftKings", "odds": "-110", "adapter": "draftkings", "conf": 93.0, "base_prob": 0.94},
        {"id": "tgt_B", "event": "FED Rate Cut", "pick": "Yes", "market": "Kalshi", "odds": "88c", "adapter": "kalshi", "conf": 91.0, "base_prob": 0.91},
        {"id": "tgt_C", "event": "FED Rate Cut", "pick": "No", "market": "Kalshi", "odds": "12c", "adapter": "kalshi", "conf": 95.0, "base_prob": 0.95}, # Should trigger contradiction resolver!
    ]

    results = []
    stats = {"received": len(raw_candidates), "simulated": 0, "confirmed_90": 0, "skipped": 0}

    for raw in raw_candidates:
        if repo.check_idempotency(raw["id"], mode):
            logger.info(f"Skipping {raw['id']} - already executed in {mode}")
            stats["skipped"] += 1
            continue

        c = Candidate(
            candidate_id=raw["id"], event_id=raw["event"], domain="sports",
            source_name="daily_scan", source_record_id=f"rec_{raw['id']}",
            source_mode=mode, source_timestamp=str(time.time()), ingested_at=str(time.time()),
            pre_simulation_confidence=raw["conf"], data_quality_score=95.0,
            features={"historical_cover_rate": raw["base_prob"], "economic_indicator_prob": raw["base_prob"]},
            event_name=raw["event"], pick=raw["pick"], market=raw["market"], live_odds=raw["odds"]
        )

        res = engine.process_candidate(c, adapter_name=raw["adapter"], seed=seed)
        repo.save_run(res)

        if res.status != "PRE_SIM_NOT_QUALIFIED":
            stats["simulated"] += 1
        if res.status == "CONFIRMED_90_PLUS":
            stats["confirmed_90"] += 1

        results.append(res)
        logger.info(f"Processed {raw['id']} -> {res.status}")

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
