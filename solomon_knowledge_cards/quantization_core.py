from typing import Any, Dict

class QuantizationCore:
    def __init__(self):
        self.supported_precisions = ["FP16", "INT8", "INT4", "1-bit"]
        self.precision_penalties = {
            "FP16": 0.0,
            "INT8": 0.05,
            "INT4": 0.15,
            "1-bit": 0.40
        }
        self.latency_threshold_ms = 2000.0

    def determine_optimal_precision(self, task_complexity: float, available_vram: float, recent_latency: float = 0.0) -> str:
        # Phase 28: Latency-Based Precision Downgrade
        if recent_latency > self.latency_threshold_ms:
            return "INT4" # Force downgrade if system is sluggish

        if available_vram > 8000 and task_complexity > 0.8:
            return "FP16"
        elif available_vram > 4000:
            return "INT8"
        else:
            return "INT4"

    def get_confidence_penalty(self, precision: str) -> float:
        return self.precision_penalties.get(precision, 0.0)

class LocalAIStack:
    def __init__(self, quant_core: QuantizationCore):
        self.quant_core = quant_core
        self.active_models: Dict[str, Any] = {}

    def load_model(self, model_name: str, task_complexity: float, vram_mb: float, latency: float = 0.0):
        precision = self.quant_core.determine_optimal_precision(task_complexity, vram_mb, latency)
        self.active_models[model_name] = {"status": "loaded", "precision": precision}
        return precision

    def execute(self, model_name: str, prompt: str) -> Dict[str, Any]:
        if model_name not in self.active_models:
            raise ValueError(f"Model {model_name} not loaded.")
        precision = self.active_models[model_name]["precision"]
        penalty = self.quant_core.get_confidence_penalty(precision)
        return {
            "result": f"Executed '{prompt[:10]}...' using {model_name} at {precision}",
            "confidence": 1.0 - penalty
        }
