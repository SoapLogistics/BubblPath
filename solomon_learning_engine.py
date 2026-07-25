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
        self.knowledge_base = {
            "patterns": [],
            "abstractions": [],
            "failures": []
        }
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    self.knowledge_base = json.load(f)
            except:
                pass

    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.knowledge_base, f, indent=4)

    def extract_pattern(self, user_input, model_output):
        """
        Extracts reusable patterns from successful interactions.
        """
        # Very basic heuristic for demonstration: if it's long, compress it.
        if len(model_output) > 200:
            pattern = {
                "trigger": user_input[:50] + "...",
                "core_concept": "Extracted concept from long response",
                "compressed_insight": model_output[:100] + "..." # Simulating compression
            }
            self.knowledge_base["patterns"].append(pattern)
            metrics_tracker.record_learning_event()
            self._save_memory()
            return True
        return False

    def compress_knowledge(self):
        """
        Quantization as Philosophy: Efficiency is intelligence. Compression is understanding.
        Merges overlapping patterns.
        """
        if len(self.knowledge_base["patterns"]) > 5:
            # Simulate compression by consolidating the last 5 patterns into 1 abstraction
            patterns_to_compress = self.knowledge_base["patterns"][-5:]
            abstraction = {
                "level": "high",
                "derived_from": len(patterns_to_compress),
                "summary": "Unified principle derived from multiple interactions."
            }
            self.knowledge_base["patterns"] = self.knowledge_base["patterns"][:-5]
            self.knowledge_base["abstractions"].append(abstraction)
            metrics_tracker.record_compression()
            self._save_memory()
            return True
        return False

    def record_failure(self, context, error_msg):
        """
        Failure is information. Failure is recorded.
        """
        self.knowledge_base["failures"].append({
            "context": context,
            "error": error_msg,
            "resolved": False
        })
        self._save_memory()

    def retrieve_context(self, user_input):
        """
        Memory exists to eliminate repeated work.
        Retrieves relevant abstractions to prepend to prompts.
        """
        if not self.knowledge_base["abstractions"]:
            return ""

        # Simple simulation: just return the latest abstraction
        latest = self.knowledge_base["abstractions"][-1]
        return f"[System Memory Context: {latest['summary']}] "

gabriel_learner = GabrielLearningEngine()
