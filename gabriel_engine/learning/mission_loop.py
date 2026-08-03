import logging
from typing import Dict, Any, List

from gabriel_engine.learning.ingestion.mission_record_ingester import MissionRecordIngester
from gabriel_engine.learning.lesson_extraction.extractor import LessonCandidateExtractor

logger = logging.getLogger("gabriel_learning")

class MissionOutcomeLearningLoop:
    """
    Mission Outcome Learning Loop v1.
    Ingests mission records, test outcomes, PR review results, deployment outcomes,
    and human feedback to produce procedure candidates, agent-performance profiles,
    and failure-prevention rules.
    """
    def __init__(self):
        self.ingester = MissionRecordIngester()
        self.extractor = LessonCandidateExtractor()

    def execute_loop(self, raw_events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        logger.info("Starting Mission Outcome Learning Loop v1.")

        # 1. Ingestion & Normalization
        normalized = self.ingester.ingest(raw_events)

        # 2. Lesson Extraction
        candidates = self.extractor.extract_candidates(normalized)

        # 3. Categorization (Output Generation)
        results = {
            "procedure_candidates": [c for c in candidates if c["type"] == "procedure"],
            "agent_performance_profiles": [c for c in candidates if c["type"] == "agent_performance_profile"],
            "failure_prevention_rules": [c for c in candidates if c["type"] == "failure_prevention_rule"]
        }

        logger.info(f"Generated {len(results['procedure_candidates'])} procedures, {len(results['agent_performance_profiles'])} agent profiles, and {len(results['failure_prevention_rules'])} failure rules.")
        return results
