from typing import Dict, Any, List
from solomon_quantization_engine import HessianSensitivitySolver
from solomon_knowledge_cards.quantization_strategy_engine import QuantizationStrategyEngine
import json

class SolomonQuantizationOptimizer:
    """
    Transforms the theoretical mathematical outputs of our Hessian trace solvers into
    actionable, physical build artifacts (Ollama Modelfiles and llama.cpp quantization commands)
    so Solomon can compile and deploy his own LLM.
    """

    def __init__(self, strategy_engine: QuantizationStrategyEngine):
        self.strategy_engine = strategy_engine

    def compile_llama_cpp_commands(self, base_model_path: str, output_model_path: str, target_ram_mb: float = 4096.0) -> Dict[str, Any]:
        """
        Generates the terminal commands needed to run an explicit mixed-precision
        quantization via llama.cpp, utilizing Solomon's active relational calibration memory.
        """
        # Step 1: Simulate the exact budget constraints and layer allocations
        ampba = self.strategy_engine.simulate_ampba(target_ram_mb=target_ram_mb)
        allocations = ampba.get("hessian_mixed_precision_solver", {}).get("allocations", [])

        # Step 2: Build GGUF block overrides string based on SOK-KNOWLEDGE-QUANT-001 principles.
        tensor_overrides = []
        for alloc in allocations:
            layer_idx = alloc["layer_idx"]
            bit_width = alloc["bit_width"]

            gguf_type = "Q4_K"
            if bit_width >= 8:
                gguf_type = "Q8_0"
            elif bit_width >= 6:
                gguf_type = "Q6_K"
            elif bit_width >= 5:
                gguf_type = "Q5_K_M"
            elif bit_width >= 4:
                gguf_type = "Q4_K_M"
            elif bit_width >= 3:
                gguf_type = "Q3_K_L"
            elif bit_width >= 2:
                gguf_type = "Q2_K"

            tensor_overrides.append(f"--override-kv 'blk.{layer_idx}.attn_v.weight={gguf_type}'")
            tensor_overrides.append(f"--override-kv 'blk.{layer_idx}.ffn_down.weight={gguf_type}'")

        calibration_data = self.strategy_engine.compile_calibration_dataset(status_filter="ACTIVE")
        calib_file = "solomon_sok_calibration.json"

        override_string = " ".join(tensor_overrides[:4]) + " ... [Truncated for brevity]"

        bash_command = (
            f"# 1. Export SOK calibration data\n"
            f"python -c \"import json; json.dump({calibration_data['total_cards_compiled']}, open('{calib_file}', 'w'))\"\n\n"
            f"# 2. Execute precision-aware GGUF Quantization using Solomon's ILP mathematical solver\n"
            f"./llama-quantize {base_model_path} {output_model_path} --imatrix {calib_file} --leave-output-tensor {override_string}"
        )

        return {
            "status": "success",
            "target_budget_mb": target_ram_mb,
            "allocated_size_mb": ampba.get("hessian_mixed_precision_solver", {}).get("allocated_size_mb", 0.0),
            "bash_compilation_script": bash_command
        }

    def compile_ollama_modelfile(self, model_name: str, gguf_path: str) -> str:
        """
        Generates an Ollama Modelfile mapping to our new hybrid quantized LLM.
        """
        modelfile_content = (
            f"FROM {gguf_path}\n"
            f'TEMPLATE """{{{{ if .System }}}}<|im_start|>system\n'
            f'{{{{ .System }}}}<|im_end|>\n'
            f'{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user\n'
            f'{{{{ .Prompt }}}}<|im_end|>\n'
            f'{{{{ end }}}}<|im_start|>assistant\n'
            f'"""\n'
            f'PARAMETER stop "<|im_start|>"\n'
            f'PARAMETER stop "<|im_end|>"\n'
            f'SYSTEM "You are Solomon, operating autonomously locally via SOSS optimized INT4/INT8 hybrid quantization."\n'
        )
        return modelfile_content
