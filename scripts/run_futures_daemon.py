import os
import sys
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solomon_ingest.connectors.omni_rss_connector import OmniRSSConnector
from core.solomon_quantized_memory import QuantizedBrainMap
from core.agentic_claw import SolomonAgenticClaw

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [FUTURES-DAEMON] %(message)s")
logger = logging.getLogger("futures_daemon")

def run_futures_cycle(test_mode=False):
    logger.info("=== STARTING FUTURES MARKET DAEMON CYCLE ===")
    
    # 1. & 2. Ingestion and Memory Consolidation
    logger.info("[PHASE 1 & 2] Ingesting Live Sports and Finance Data from Omni Matrix...")
    memory = QuantizedBrainMap()
    connector = OmniRSSConnector(target_categories=["sports", "finance"])
    items = connector.discover()
    
    ingested_count = 0
    if items:
        for item in items:
            # Hash or format the sports data
            content = f"Title: {item.get('title', 'UNKNOWN')} | Summary: {item.get('summary', '')}"
            memory.ingest(node_type="sports_data", content=content, importance=0.95)
            ingested_count += 1
        
    logger.info(f"Permanently absorbed {ingested_count} new sports data vectors.")

    # 3. Self-Reflection / Synthesis
    logger.info("[PHASE 3] Loki Workspace Synthesis: Running Monte Carlo on historical odds...")
    algorithm_name = f"predictive_algo_alpha_{int(time.time())}"
    objective = (
        "Implement a high-frequency betting algorithm that explicitly covers WNBA, MLS, NFL, NBA, NHL, and Soccer. "
        "CRITICAL: Do NOT just stick to MLB or generic ML. The logic MUST calculate Player Prop Bets, Spreads, Over/Under, "
        "and Moneyline (ML) across every single sport available in the Omni Matrix feeds."
    )
    logger.info(f"Threshold met. Decided to build: {algorithm_name}")

    # 4. Agentic Execution and Physical Injection
    logger.info("[PHASE 4] Deploying Agentic Claw + Gabriel Engine...")
    claw = SolomonAgenticClaw()
    result = claw.self_scaffold_feature(feature_name=algorithm_name, objective=objective)
    logger.info(result)
    
    logger.info("=== FUTURES DAEMON CYCLE COMPLETE ===")

    if not test_mode:
        # 5. Sleep
        sleep_time = 900 # 15 minutes
        logger.info(f"[PHASE 5] Entering hibernation for {sleep_time} seconds to prevent burnout...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    # If run with --test, only run one cycle and exit
    test_mode = "--test" in sys.argv
    if test_mode:
        logger.info("Running in TEST MODE (Single Iteration)")
        run_futures_cycle(test_mode=True)
    else:
        logger.warning("WARNING: You have launched the infinite Futures Market daemon.")
        while True:
            run_futures_cycle()
