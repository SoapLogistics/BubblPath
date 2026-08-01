import logging
from typing import Dict, Any
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

        # 2. Knowledge Graph / Abstraction & Horizon Evaluation
        if "facts" in event_data:
            fact_ids = [self.pat_memory.ingest_raw_fact(f) for f in event_data["facts"]]
            if "concept" in event_data:
                 concept = event_data["concept"]
                 parent_id = self.pat_memory.abstract_cluster(fact_ids, concept)
                 results["subsystem_results"]["abstraction"] = f"abstracted_node_{parent_id}"

                 # ENHANCEMENT: Evaluate the novelty of this newly abstracted concept
                 horizon_eval = self.research_horizon.analyze_novelty_opportunity(concept)
                 results["subsystem_results"]["horizon_eval"] = horizon_eval

        # 3. Tool Learning / Capability Assimilation
        if event_type == "tool_usage" or "tool_logs" in event_data:
            tool_name = event_data.get("tool_name", "unknown_tool")
            tool_logs = event_data.get("tool_logs", "")
            assimilation_result = self.capability.analyze_tool_workflow(tool_name, tool_logs)
            results["subsystem_results"]["capability"] = assimilation_result

            # ENHANCEMENT: If capability successfully assimilated, simulate regression test
            if assimilation_result.get("status") == "success":
                regression_passed = self.self_eval.simulate_regression_test(tool_name)
                results["subsystem_results"]["regression_test"] = regression_passed

        # 4. Failure Analysis & Self-Healing
        if event_type == "failure" or event_data.get("status") == "error":
            anti_patterns = self.meta_learner.analyze_failure_patterns([event_record])
            results["subsystem_results"]["failure_analysis"] = anti_patterns
            if "code" in event_data:
                eval_result = self.self_eval.red_team_adversarial_review(event_data["code"])
                results["subsystem_results"]["self_eval"] = eval_result

        # 5. Curiosity, World Model, & Distributed Swarm Trigger
        predicted_outcome = event_data.get("predicted_outcome")
        actual_outcome = event_data.get("actual_outcome")
        if predicted_outcome and actual_outcome:
            surprise = self.curiosity.evaluate_surprise(str(event_data), actual_outcome, predicted_outcome)
            results["subsystem_results"]["curiosity_surprise"] = surprise
            if surprise > 0.5:
                concept_gap = event_data.get("concept_gap", f"Gap_from_{event_type}")
                self.curiosity.add_to_frontier(concept_gap)

                # ENHANCEMENT: High surprise triggers a swarm deep-dive
                swarm_task = f"Deep dive research into anomaly: {concept_gap}"
                swarm_result = self.swarm.delegate_task(swarm_task, "Researcher")
                results["subsystem_results"]["swarm_delegation"] = swarm_result

        # 6. Meta-Learning Optimization
        if "prompt" in event_data and "success_score" in event_data:
            optimized_prompt = self.meta_learner.optimize_prompt(
                event_data["prompt"],
                event_data.get("context", ""),
                event_data["success_score"]
            )
            self.meta_learner.tune_retrieval_parameters(event_type, event_data["success_score"])
            results["subsystem_results"]["meta_learner"] = "prompt_optimized"

        # 7. Experience Replay, Sleep Thresholds, & Evolutionary Advance
        if len(self.memory.episodic_memory) > 10:  # Threshold for sleep
            sleep_result = self.memory.trigger_sleep_consolidation()
            results["subsystem_results"]["sleep_consolidation"] = sleep_result

            # ENHANCEMENT: If massive consolidation occurs, advance roadmap phase
            if sleep_result.get("consolidated_events", 0) > 20:
                roadmap_status = self.roadmap.advance_phase()
                results["subsystem_results"]["roadmap_advance"] = roadmap_status

        # 8. Optimization & Efficiency Tick
        if event_type == "query":
            route_result = self.efficiency.route_moe_query(event_data.get("query", ""))
            results["subsystem_results"]["moe_route"] = route_result

        # ENHANCEMENT: Universal optimizer tick for every event
        self.optimizer.run_optimization_cycle()
        results["subsystem_results"]["optimizer_tick"] = "completed"

        return results
