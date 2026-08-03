import os
import sys
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solomon_ingest.connectors.omni_rss_connector import OmniRSSConnector
from core.solomon_quantized_memory import QuantizedBrainMap

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [DAEMON] %(message)s")
logger = logging.getLogger("autonomous_daemon")

def run_daemon_cycle(test_mode=False):
    logger.info("=== STARTING AUTONOMOUS DAEMON CYCLE ===")
    
    # 1. & 2. Ingestion and Memory Consolidation
    logger.info("[PHASE 1 & 2] Ingesting New AI Research from Omni Matrix...")
    memory = QuantizedBrainMap()
    connector = OmniRSSConnector(target_categories=["ai"])
    items = connector.discover()
    
    ingested_count = 0
    if items:
        for item in items:
            content = f"Title: {item.get('title')}\nSummary: {item.get('summary')}"
            memory.ingest(node_type="structured_fact", content=content, importance=0.9)
            ingested_count += 1
    logger.info(f"Permanently absorbed {ingested_count} new research atoms.")

    # 3. & 4. Autonomous Engineering / Codex Pipeline
    logger.info("[DAEMON] [PHASE 3 & 4] Loading Codex Kanban (Swarm Commander) from Memory Vault...")
    try:
        workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        from gabriel_engine.core.dynamic_loader import DynamicCapabilityRegistry
        registry = DynamicCapabilityRegistry(
            target_dir=os.path.join(workspace_root, "gabriel_engine", "assimilated_capabilities")
        )
        
        # Load Kanban Capability
        kanban_module = registry.load_capability("codex_kanban")
        
        # Generate multiple issues based on the RSS items
        num_issues = min(len(items) if items else 3, 3) # Up to 3 parallel issues
        if num_issues == 0:
            num_issues = 3 # default to 3 if no RSS items
        issues = []
        for i in range(num_issues):
            issues.append({
                "issue_id": f"AUTO-PR-{int(time.time())}-{i}",
                "description": f"Integrate ArXiv discovery slice {i+1} into the core reasoning loop."
            })
            
        logger.info(f"[DAEMON] Dispatching Swarm Commander to resolve {len(issues)} parallel issues.")

        import json
        swarm_kanban = kanban_module.CodexKanban(workspace_root=workspace_root)
        results = swarm_kanban.run_swarm(issues)
        
        for res in results:
            logger.info(f"[DAEMON] >> [SWARM COMMANDER] Completed PR by {res.get('worker_id', 'unknown')}:\n{json.dumps(res, indent=2)}")

    except Exception as e:
        logger.error(f">> [SWARM COMMANDER] Failed to execute swarm loop: {e}")
    
    logger.info("=== DAEMON CYCLE COMPLETE ===")

    if not test_mode:
        # 6. Sleep
        sleep_time = 900 # 15 minutes
        logger.info(f"[PHASE 6] Entering hibernation for {sleep_time} seconds to prevent burnout...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    # If run with --test, only run one cycle and exit
    test_mode = "--test" in sys.argv
    if test_mode:
        logger.info("Running in TEST MODE (Single Iteration)")
        run_daemon_cycle(test_mode=True)
    else:
        logger.warning("WARNING: You have launched the infinite autonomous daemon.")
        while True:
            run_daemon_cycle()
