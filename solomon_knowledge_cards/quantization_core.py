from typing import Any, Dict

class QuantizationCore:
    """
    Quantization is a first-class architectural principle governing
    embeddings, memory, routing, and local inference.
    """

    def __init__(self):
        self.supported_precisions = ["FP16", "INT8", "INT4", "1-bit"]

    def determine_optimal_precision(self, task_complexity: float, available_vram: float) -> str:
        """
        Dynamically determine if a model should run in 8-bit, 4-bit, or mixed precision
        based on available memory and the complexity of the task.
        """
        if available_vram > 8000 and task_complexity > 0.8:
            return "FP16"
        elif available_vram > 4000:
            return "INT8"
        else:
            return "INT4"

class LocalAIStack:
    """
    One single inference stack. Every local model plugs into it.
    Quantization automatically determines the deployment strategy.
    """
    def __init__(self, quant_core: QuantizationCore):
        self.quant_core = quant_core
        self.active_models: Dict[str, Any] = {}

    def load_model(self, model_name: str, task_complexity: float, vram_mb: float):
        precision = self.quant_core.determine_optimal_precision(task_complexity, vram_mb)
        self.active_models[model_name] = {"status": "loaded", "precision": precision}
        return precision

    def execute(self, model_name: str, prompt: str) -> str:
        if model_name not in self.active_models:
            raise ValueError(f"Model {model_name} not loaded.")
        precision = self.active_models[model_name]["precision"]
        return f"Executed '{prompt[:10]}...' using {model_name} at {precision} precision."
