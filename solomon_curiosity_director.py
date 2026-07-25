import json
import os

class CuriosityDirector:
    """
    Implements 'Curiosity' from the Manifesto.
    Curiosity is not random exploration; it is disciplined investigation.
    Continuously maps the frontier between Known and Unknown.
    """
    def __init__(self, memory_file="gabriel_knowledge_base.json"):
        self.memory_file = memory_file

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"patterns": [], "abstractions": [], "failures": [], "research_queue": []}

    def _save_memory(self, data):
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=4)

    def scan_frontier(self):
        """
        Scans memory for failures and low-confidence abstractions to generate research tasks.
        """
        memory = self._load_memory()
        research_queue = memory.setdefault("research_queue", [])
        new_tasks = 0

        # 1. Investigate Repeated Failures
        failures = memory.get("failures", [])
        unresolved_failures = [f for f in failures if not f.get("resolved", False)]

        if len(unresolved_failures) > 3:
            # Consolidate failures into a research task
            task = {
                "type": "investigate_failure_cluster",
                "target": unresolved_failures[0]["error"],
                "urgency": "high",
                "reason": "System is repeatedly failing with the same error. Requires a new capability or heuristic."
            }
            # Prevent duplicate tasks
            if not any(t.get("target") == task["target"] for t in research_queue):
                research_queue.append(task)
                new_tasks += 1

        # 2. Investigate Low-Confidence Abstractions (The Known Unknown)
        abstractions = memory.get("abstractions", [])
        low_confidence = [a for a in abstractions if a.get("confidence", 1.0) < 0.5]

        for a in low_confidence:
            task = {
                "type": "validate_assumption",
                "target": a["concept"],
                "urgency": "medium",
                "reason": "Abstraction exists but lacks sufficient evidentiary backing. Needs testing."
            }
            if not any(t.get("target") == task["target"] for t in research_queue):
                research_queue.append(task)
                new_tasks += 1

        memory["research_queue"] = research_queue
        self._save_memory(memory)

        return {
            "status": "success",
            "new_research_tasks_generated": new_tasks,
            "total_queue_size": len(research_queue)
        }

curiosity_director = CuriosityDirector()
