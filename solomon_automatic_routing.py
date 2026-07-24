from typing import Dict, Any, List
from solomon_performance_predictor import PerformancePredictor
from solomon_model_router import ModelRouter
from solomon_mnemosyne_db import SolomonMnemosyneDB

class AutomaticRoutingEngine:
    """
    Priority 7: Quantization Automatic Routing Logic.
    """

    def __init__(self, db=None):
        if db is None:
            self.db = SolomonMnemosyneDB()
        else:
            self.db = db
        self.router = ModelRouter(self.db)

    def measure_ram_usage(self, num_parameters: float, precision_bits: int, context_tokens: int) -> float:
        """
        Measure expected RAM usage.
        """
        metrics = PerformancePredictor.predict_performance_metrics(num_parameters, precision_bits, context_tokens)
        return metrics["total_predicted_footprint_mb"]

    def benchmark_latency(self, num_parameters: float, precision_bits: int, context_tokens: int) -> float:
        """
        Benchmark expected latency.
        """
        metrics = PerformancePredictor.predict_performance_metrics(num_parameters, precision_bits, context_tokens)
        return metrics["predicted_latency_per_token_ms"]

    def benchmark_accuracy(self, num_parameters: float, precision_bits: int, context_tokens: int) -> float:
        """
        Benchmark expected accuracy/quality.
        """
        metrics = PerformancePredictor.predict_performance_metrics(num_parameters, precision_bits, context_tokens)
        return metrics["estimated_reasoning_quality"]

    def determine_routing_thresholds(self, available_ram_mb: float, target_latency_ms: float, target_accuracy: float) -> Dict[str, float]:
        """
        Determine routing thresholds dynamically based on available resources and goals.
        """
        # A simple heuristic to compute a routing threshold
        # If RAM is low, we want a higher threshold (more likely to route to quantized model)
        base_threshold = 0.15
        if available_ram_mb < 2000.0:
            base_threshold += 0.2  # Increase threshold to force more queries to Quantized

        if target_latency_ms < 20.0:
            base_threshold += 0.1  # Need faster model, increase threshold for high-precision

        if target_accuracy > 90.0:
            base_threshold -= 0.15 # Need high accuracy, lower threshold so more go to High-Precision

        return {"dynamic_threshold": max(0.05, min(0.95, base_threshold))}

    def identify_where_quantized_models_can_replace_full_precision(self, available_ram_mb: float) -> List[str]:
        """
        Identify scenarios/queries where quantized models can replace full precision.
        """
        scenarios = []
        if available_ram_mb < 4000:
            scenarios.append("Low RAM environments (< 4GB)")
        scenarios.append("High-throughput summarization tasks")
        scenarios.append("Standard conversational queries with high card confidence")
        scenarios.append("Drafting phase of speculative decoding")
        return scenarios

    def create_automatic_routing_logic(self, query: str, available_ram_mb: float, target_latency_ms: float = 50.0, target_accuracy: float = 85.0) -> Dict[str, Any]:
        """
        Create the full automatic routing logic tying the steps together.
        """
        thresholds = self.determine_routing_thresholds(available_ram_mb, target_latency_ms, target_accuracy)
        effective_threshold = thresholds["dynamic_threshold"]

        routing_decision = self.router.route_query(query, threshold=effective_threshold)

        # We can also cross-reference if the quantized model can replace full precision
        scenarios = self.identify_where_quantized_models_can_replace_full_precision(available_ram_mb)

        return {
            "query": query,
            "available_ram_mb": available_ram_mb,
            "applied_threshold": effective_threshold,
            "routing_decision": routing_decision,
            "quantized_replacement_scenarios": scenarios
        }
