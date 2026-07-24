import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger("SPLE_Memory")

class SPLEMemoryManager:
    """
    Handles Part 8 of the SPLE blueprint: Memory.
    Manages multi-tiered architecture and sleep consolidation.
    """
    def __init__(self):
        self.working_memory: List[Dict[str, Any]] = []
        self.episodic_memory: List[Dict[str, Any]] = []
        self.semantic_memory: Dict[str, Any] = {} # Simulated Knowledge Graph
        self.sleep_cycle_active: bool = False
        logger.info("SPLE Memory Manager initialized with tiered architecture.")

    def store_episodic(self, event: Dict[str, Any]):
        """Logs an event into short-term episodic memory."""
        event["timestamp"] = time.time()
        self.episodic_memory.append(event)
        logger.debug(f"Stored episodic event: {event.get('type', 'unknown')}")

    def trigger_sleep_consolidation(self) -> Dict[str, Any]:
        """
        Executes the 'sleep' cycle: replays episodic memory, extracts semantic rules,
        updates weights, and prunes old data.
        """
        self.sleep_cycle_active = True
        logger.info("Initiating Sleep Consolidation Cycle...")

        consolidated_count = 0
        for event in self.episodic_memory:
            # Simulate semantic abstraction
            concept_key = f"Concept_{event.get('type', 'generic')}"
            if concept_key not in self.semantic_memory:
                self.semantic_memory[concept_key] = {"occurrences": 1, "abstract_rule": f"Rule derived from {concept_key}"}
            else:
                self.semantic_memory[concept_key]["occurrences"] += 1
            consolidated_count += 1

        # Clear episodic memory after consolidation (simulate pruning/decay)
        self.episodic_memory.clear()
        self.sleep_cycle_active = False

        result = {"status": "success", "consolidated_events": consolidated_count, "semantic_nodes": len(self.semantic_memory)}
        logger.info(f"Sleep cycle complete. {result}")
        return result

    def query_semantic_memory(self, query: str) -> Dict[str, Any]:
        """Simulates retrieval from the deeply consolidated Knowledge Graph."""
        logger.info(f"Querying semantic memory for: {query}")
        # Dummy retrieval logic
        for key, data in self.semantic_memory.items():
            if query.lower() in key.lower():
                return data
        return {"result": "Not found in consolidated memory"}
