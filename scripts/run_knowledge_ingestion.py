import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.solomon_quantized_memory import QuantizedBrainMap
from solomon_ingest.connectors.official_rss_connector import OfficialRSSConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [KNOWLEDGE_INGEST] %(message)s")
logger = logging.getLogger("knowledge_ingest")

def run():
    logger.info("Initializing Solomon Knowledge Ingestion Sequence...")
    
    # 1. Connect to Memory
    memory = QuantizedBrainMap()
    logger.info("Connected to Hyper-Quantized SQLite Brain.")
    
    # 2. Spin up the RSS Connector
    connector = OfficialRSSConnector()
    logger.info(f"Targeting AI Research via {connector.source_id}")
    
    # 3. Discover and Fetch
    logger.info("Extracting data from Tier A sources...")
    items = connector.discover()
    
    if not items:
        logger.warning("No items extracted. The ingestion sequence aborted.")
        return
        
    logger.info(f"Successfully extracted {len(items)} knowledge atoms.")
    
    # 4. Inject into Memory
    ingested_count = 0
    for item in items:
        # We format the content so the LLM can use it logically
        content = f"Title: {item.get('title')}\nSummary: {item.get('summary')}\nSource: {item.get('url')}"
        
        try:
            memory.ingest(
                node_type="structured_fact", 
                content=content,
                importance=0.9, # AI research is highly important to him
                valence=0.0,
                arousal=0.5
            )
            ingested_count += 1
        except Exception as e:
            logger.error(f"Failed to ingest knowledge atom: {e}")
            
    logger.info(f"Knowledge Ingestion Complete. {ingested_count} atoms permanently burned into memory.")

if __name__ == "__main__":
    run()
