import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EfficiencyMetrics:
    def __init__(self):
        self.tokens_used = 0
        self.time_spent = 0.0
        self.memory_bytes = 0

class QuantizationOptimizer:
    """
    Implements the Solomon Efficiency Doctrine (SED).
    Prioritizes 'elegant efficiency' - tracking Learning Return on Investment (LROI)
    and suggesting structural compressions over purely numerical quantization.
    """
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def record_task_cost(self, task_type: str, metrics: EfficiencyMetrics, success: bool):
        self.history.append({
            "type": task_type,
            "tokens": metrics.tokens_used,
            "time": metrics.time_spent,
            "success": success
        })

    def calculate_lroi(self, task_type: str) -> float:
        """
        Learning Return on Investment.
        Compares the cost of solving similar tasks before a skill was acquired
        vs. after it was acquired (or just compares early vs recent instances).
        Returns > 1.0 if efficiency is improving.
        """
        relevant = [h for h in self.history if h["type"] == task_type and h["success"]]
        if len(relevant) < 2:
            return 1.0 # Baseline

        # Compare the average cost of the first half to the second half
        mid = len(relevant) // 2
        early = relevant[:mid]
        recent = relevant[mid:]

        avg_early_tokens = sum(x["tokens"] for x in early) / len(early)
        avg_recent_tokens = sum(x["tokens"] for x in recent) / len(recent)

        if avg_recent_tokens == 0:
            return float('inf')

        lroi = avg_early_tokens / avg_recent_tokens
        logger.info(f"LROI for {task_type}: {lroi:.2f}")
        return lroi

    def suggest_compression(self, task_type: str) -> List[str]:
        """
        Analyzes task history and suggests structural quantization strategies.
        """
        suggestions = []
        lroi = self.calculate_lroi(task_type)

        relevant = [h for h in self.history if h["type"] == task_type]

        if not relevant:
            return ["No data available for optimization."]

        avg_tokens = sum(x["tokens"] for x in relevant) / len(relevant)
        success_rate = sum(1 for x in relevant if x["success"]) / len(relevant)

        if success_rate > 0.9 and lroi < 1.1:
            suggestions.append(f"Skill '{task_type}' is highly stable. Package into a fixed deterministic procedure to bypass LLM token costs entirely (Workflow Quantization).")

        if avg_tokens > 5000:
            suggestions.append(f"High token usage detected in '{task_type}'. Implement semantic context pruning before routing to LLM (Context Quantization).")

        return suggestions
