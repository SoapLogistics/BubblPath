import logging
import uuid
import concurrent.futures
from typing import Dict, Any, List, Optional
from solomon_core.interfaces import IWorkerSwarm
from solomon_core.event_bus import CognitiveEventBus

logger = logging.getLogger("GabrielTaskRouter")

from solomon_core.gabriel.worker import GabrielWorker
from solomon_core.gabriel.arbiter import SwarmArbiter

class GabrielTaskRouter(IWorkerSwarm):
    """
    Advanced Gabriel Task Router for Project Solomon.
    Implements multi-agent swarm delegation, sub-agent roles, and LLM-driven consensus mechanics.
    """
    def __init__(self):
        self.bus = CognitiveEventBus()
        self.arbiter = SwarmArbiter()

        # Define the personas comprising the swarm
        self.workers = {
            "Architect": GabrielWorker("Architect", "You are the Architect. Focus on structural design, system boundaries, and scalability."),
            "Researcher": GabrielWorker("Researcher", "You are the Researcher. Focus on finding theoretical algorithms, edge cases, and external data requirements."),
            "Builder": GabrielWorker("Builder", "You are the Builder. Focus on concrete implementation, clean code patterns, and practical execution.")
        }

    def execute_task(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Routes a task to multiple agents and forces consensus on the output via the Arbiter."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        logger.info(f"Gabriel Router dispatching task {task_id}")

        # 1. Swarm Execution (Parallel)
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.workers)) as executor:
            future_to_role = {
                executor.submit(self.workers[role].generate, prompt, context): role
                for role in self.workers
            }
            for future in concurrent.futures.as_completed(future_to_role):
                role = future_to_role[future]
                try:
                    results[role] = future.result()
                except Exception as exc:
                    logger.error(f"Worker {role} generated an exception: {exc}")
                    results[role] = "FAILED"

        # 2. BFT Consensus Resolution (LLM Synthesis)
        final_consensus = self.arbiter.synthesize(prompt, results)

        payload = {
            "task_id": task_id,
            "consensus_output": final_consensus,
            "swarm_diagnostics": results
        }

        # 3. Publish to Event Bus
        self.bus.publish("SwarmTaskCompleted", payload)
        return payload

    def health_check(self) -> bool:
        return True
