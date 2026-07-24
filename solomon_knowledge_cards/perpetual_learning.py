from typing import Any, Dict
import hashlib

class CuriosityEngine:
    def __init__(self):
        self.research_queue = []

    def ingest_failure(self, task: Dict[str, Any], error: str):
        self.research_queue.append({"type": "failure_analysis", "task": task, "error": error})

    def trigger_autonomous_research(self):
        if not self.research_queue:
            return None
        item = self.research_queue.pop(0)
        return {"status": "researched", "findings": f"Resolved {item['type']} for {item.get('task')}"}

class SkillAssimilation:
    def __init__(self):
        self.skill_registry = {}

    def extract_and_index_skill(self, problem_description: str, solution_code: str):
        skill_hash = hashlib.sha256(solution_code.encode()).hexdigest()
        self.skill_registry[skill_hash] = {
            "problem": problem_description,
            "skill": solution_code,
            "benchmark_score": 1.0
        }
        return skill_hash

class ContinuousLearningPipeline:
    def __init__(self, curiosity: CuriosityEngine, skills: SkillAssimilation):
        self.curiosity = curiosity
        self.skills = skills

    def ingest(self, result: Dict[str, Any]):
        if result.get("status") == "failure":
            self.curiosity.ingest_failure(result.get("task", {}), result.get("error", "Unknown"))
        elif result.get("solution_code"):
            self.skills.extract_and_index_skill(result.get("problem", ""), result.get("solution_code"))
