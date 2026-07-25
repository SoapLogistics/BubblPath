import json
import os
from solomon_metrics import metrics_tracker

class GabrielLearningEngine:
    """
    Implements the Gabriel Engine Manifesto: The Law of Compounding Learning.
    Every task completed should improve the next task.
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
        return {
            "patterns": [],
            "abstractions": [],
            "failures": [],
            "research_queue": []
        }

    def _save_memory(self, memory):
        with open(self.memory_file, "w") as f:
            json.dump(memory, f, indent=4)

    def extract_pattern(self, user_input, model_output):
        """
        Extracts reusable patterns from successful interactions.
        """
        memory = self._load_memory()

        # Very basic heuristic for demonstration: if it's long, compress it.
        if len(model_output) > 200:
            pattern = {
                "trigger": user_input[:50] + "...",
                "core_concept": "Extracted concept from long response",
                "compressed_insight": model_output[:100] + "..." # Simulating compression
            }
            memory.setdefault("patterns", []).append(pattern)
            metrics_tracker.record_learning_event()
            self._save_memory(memory)
            return True
        return False

    def record_failure(self, context, error_msg):
        """
        Failure is information. Failure is recorded.
        """
        memory = self._load_memory()
        memory.setdefault("failures", []).append({
            "context": context,
            "error": error_msg,
            "resolved": False
        })
        self._save_memory(memory)

    def retrieve_context(self, user_input):
        """
        Memory exists to eliminate repeated work.
        Retrieves relevant abstractions to prepend to prompts.
        """
        memory = self._load_memory()
        abstractions = memory.get("abstractions", [])
        if not abstractions:
            return ""

        # Simple simulation: just return the latest abstraction
        latest = abstractions[-1]
        return f"[System Memory Context: {latest['summary']}] "

gabriel_learner = GabrielLearningEngine()
