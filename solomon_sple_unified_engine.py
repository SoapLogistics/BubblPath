import logging
from typing import Dict, Any, List
import time

from solomon_meta_learner import MetaLearner
from solomon_curiosity_engine import CuriosityEngine
from solomon_sple_memory import SPLEMemoryManager
from solomon_sple_capability import CapabilityAssimilator
from solomon_sple_self_eval import SelfEvaluationEngine
from solomon_sple_pat_memory import ProgressiveAbstractionTree
from solomon_sple_optimizer import SPLEOptimizer
from solomon_sple_efficiency import LearningEfficiencyEngine
from solomon_sple_world_model import WorldModelSimulator
from solomon_sple_roadmap import EvolutionaryRoadmapPlanner
from solomon_sple_distributed import DistributedSwarmManager
from solomon_sple_research_horizon import ResearchHorizonPredictor

logger = logging.getLogger("PerpetualLearningEngine")

class PerpetualLearningEngine:
    """
    Unified learning pipeline that connects all SPLE subsystems.
    Every learning event goes through this single pipeline.
    """
    def __init__(self):
        # Initialize all subsystems here rather than disjointedly in app.py
        self.meta_learner = MetaLearner()
        self.curiosity = CuriosityEngine()
        self.memory = SPLEMemoryManager()
        self.capability = CapabilityAssimilator()
        self.self_eval = SelfEvaluationEngine()
        self.pat_memory = ProgressiveAbstractionTree()
        self.optimizer = SPLEOptimizer()
        self.efficiency = LearningEfficiencyEngine()
        self.world_model = WorldModelSimulator()
        self.roadmap = EvolutionaryRoadmapPlanner()
        self.swarm = DistributedSwarmManager()
        self.research_horizon = ResearchHorizonPredictor()
        logger.info("PerpetualLearningEngine (Unified Pipeline) initialized.")

    def process_learning_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        The single entry point for all learning events.
        """
        logger.info(f"Processing unified learning event: {event_type}")
        results = {"event_type": event_type, "status": "processed", "subsystem_results": {}}

        # 1. Ingestion & Memory Logging
        event_record = {"type": event_type, "data": event_data, "timestamp": time.time()}
        self.memory.store_episodic(event_record)
        results["subsystem_results"]["memory"] = "stored_episodic"

        # 2. Knowledge Graph / Abstraction
        if "facts" in event_data:
            fact_ids = [self.pat_memory.ingest_raw_fact(f) for f in event_data["facts"]]
            if "concept" in event_data:
                 parent_id = self.pat_memory.abstract_cluster(fact_ids, event_data["concept"])
                 results["subsystem_results"]["abstraction"] = f"abstracted_node_{parent_id}"

        # 3. Tool Learning / Capability Assimilation
        if event_type == "tool_usage" or "tool_logs" in event_data:
            tool_name = event_data.get("tool_name", "unknown_tool")
            tool_logs = event_data.get("tool_logs", "")
            assimilation_result = self.capability.analyze_tool_workflow(tool_name, tool_logs)
            results["subsystem_results"]["capability"] = assimilation_result

        # 4. Failure Analysis & Self-Healing
        if event_type == "failure" or event_data.get("status") == "error":
            anti_patterns = self.meta_learner.analyze_failure_patterns([event_record])
            results["subsystem_results"]["failure_analysis"] = anti_patterns
            if "code" in event_data:
                eval_result = self.self_eval.red_team_adversarial_review(event_data["code"])
                results["subsystem_results"]["self_eval"] = eval_result

        # 5. Curiosity & World Model
        predicted_outcome = event_data.get("predicted_outcome")
        actual_outcome = event_data.get("actual_outcome")
        if predicted_outcome and actual_outcome:
            surprise = self.curiosity.evaluate_surprise(str(event_data), actual_outcome, predicted_outcome)
            results["subsystem_results"]["curiosity_surprise"] = surprise
            if surprise > 0.5:
                concept_gap = event_data.get("concept_gap", f"Gap_from_{event_type}")
                self.curiosity.add_to_frontier(concept_gap)

        # 6. Meta-Learning Optimization
        if "prompt" in event_data and "success_score" in event_data:
            optimized_prompt = self.meta_learner.optimize_prompt(
                event_data["prompt"],
                event_data.get("context", ""),
                event_data["success_score"]
            )
            self.meta_learner.tune_retrieval_parameters(event_type, event_data["success_score"])
            results["subsystem_results"]["meta_learner"] = "prompt_optimized"

        # 7. Experience Replay / Sleep Thresholds
        if len(self.memory.episodic_memory) > 10:  # Threshold for sleep
            sleep_result = self.memory.trigger_sleep_consolidation()
            results["subsystem_results"]["sleep_consolidation"] = sleep_result

        # 8. Optimization & Efficiency
        if event_type == "query":
            route_result = self.efficiency.route_moe_query(event_data.get("query", ""))
            results["subsystem_results"]["moe_route"] = route_result

        return results
