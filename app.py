import os
import openai
from flask import Flask, request, jsonify
from solomon_knowledge_cards.gabriel_kernel import GabrielKernel, OpenAIWorker
from solomon_knowledge_cards.unified_knowledge_graph import UniversalKnowledgeGraph, UnifiedEmbeddingEngine
from solomon_knowledge_cards.dynamic_context import DynamicContextEngine
from solomon_knowledge_cards.quantization_core import QuantizationCore, LocalAIStack
from solomon_knowledge_cards.perpetual_learning import CuriosityEngine, SkillAssimilation, ContinuousLearningPipeline
from solomon_knowledge_cards.solomon_runtime import SolomonOSKernel
from solomon_knowledge_cards.recursive_optimizer import RecursiveOptimizer

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- INITIALIZE THE CONVERGED SOLOMON OS KERNEL ---
quant_core = QuantizationCore()
ai_stack = LocalAIStack(quant_core)
ai_stack.load_model("default-llm", task_complexity=0.5, vram_mb=2000)

graph = UniversalKnowledgeGraph()
embed_engine = UnifiedEmbeddingEngine()

context_engine = DynamicContextEngine(max_vram_mb=2000)

curiosity = CuriosityEngine()
skills = SkillAssimilation()
learning_pipeline = ContinuousLearningPipeline(curiosity, skills)

gabriel = GabrielKernel()
# Register the actual functional OpenAI worker instead of a dummy
gabriel.register_worker("openai", OpenAIWorker())
gabriel.set_learning_pipeline(learning_pipeline)

solomon_os = SolomonOSKernel(gabriel, graph, context_engine, ai_stack, learning_pipeline)
optimizer = RecursiveOptimizer(solomon_os.dashboard)
# --------------------------------------------------


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    # Use the unified OS Kernel to route the task to the OpenAIWorker
    task = {
        "instruction": "chat_response",
        "messages": [{"role": "user", "content": user_message}],
        "required_capability": "chat"
    }

    result = solomon_os.execute_workload(task)

    # Run background optimization
    opt_status = optimizer.evaluate_system_performance()

    return jsonify({
        "reply": result.get("result", ""),
        "system_health": solomon_os.dashboard.get_system_health(),
        "optimization": opt_status
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
