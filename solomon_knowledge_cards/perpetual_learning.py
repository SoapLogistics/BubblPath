from typing import Any, Dict, List, Optional
import hashlib
import time
import heapq

class CuriosityEngine:
    def __init__(self):
        # Phase 26: Priority Curiosity Queue
        # We use a heap to sort by severity (lower number = higher priority)
        self.research_queue = []
        self.counter = 0

    def ingest_failure(self, task: Dict[str, Any], error: str, severity: int = 5):
        hypothesis = f"Hypothesis: Worker failed due to context limitation or unsupported complexity. Error: {error}"
        item = {"type": "hypothesis_generation", "task": task, "hypothesis": hypothesis}
        heapq.heappush(self.research_queue, (severity, self.counter, item))
        self.counter += 1

    def trigger_autonomous_research(self) -> Optional[Dict[str, Any]]:
        if not self.research_queue:
            return None
        _, _, item = heapq.heappop(self.research_queue)
        return {"status": "researched", "findings": item["hypothesis"]}

class SkillAssimilation:
    def __init__(self):
        self.skill_registry = {}
        # Phase 25: Skill Dependency Chaining
        self.skill_dependencies: Dict[str, List[str]] = {}

    def extract_and_index_skill(self, problem_description: str, solution_code: str, deps: List[str] = None):
        skill_hash = hashlib.sha256(solution_code.encode()).hexdigest()
        self.skill_registry[skill_hash] = {
            "problem": problem_description,
            "skill": solution_code,
            "benchmark_score": 1.0,
            "last_benchmarked": time.time()
        }
        if deps:
            self.skill_dependencies[skill_hash] = deps
        return skill_hash

    def benchmark_skills(self):
        for sk_hash, data in self.skill_registry.items():
            data["benchmark_score"] = min(data["benchmark_score"] + 0.1, 1.0)
            data["last_benchmarked"] = time.time()

class ContinuousLearningPipeline:
    def __init__(self, curiosity: CuriosityEngine, skills: SkillAssimilation):
        self.curiosity = curiosity
        self.skills = skills

    def ingest(self, result: Dict[str, Any]):
        if result.get("status") == "error":
            severity = 1 if "Critical" in result.get("error_message", "") else 5
            self.curiosity.ingest_failure(result.get("task", {}), result.get("error_message", "Unknown"), severity)
        elif result.get("solution_code"):
            self.skills.extract_and_index_skill(result.get("problem", ""), result.get("solution_code"), result.get("dependencies"))
