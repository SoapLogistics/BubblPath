import os
import openai
from flask import Flask, request, jsonify
from solomon_knowledge_cards.gabriel_kernel import GabrielKernel, OpenAIWorker, LocalStubWorker
from solomon_knowledge_cards.unified_knowledge_graph import UniversalKnowledgeGraph, UnifiedEmbeddingEngine
from solomon_knowledge_cards.dynamic_context import DynamicContextEngine
from solomon_knowledge_cards.quantization_core import QuantizationCore, LocalAIStack
from solomon_knowledge_cards.perpetual_learning import CuriosityEngine, SkillAssimilation, ContinuousLearningPipeline
from solomon_knowledge_cards.solomon_runtime import SolomonOSKernel
from solomon_knowledge_cards.recursive_optimizer import RecursiveOptimizer

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY", "dummy")

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
gabriel.register_worker("openai", OpenAIWorker())
gabriel.register_worker("local_stub", LocalStubWorker())
gabriel.set_learning_pipeline(learning_pipeline)

solomon_os = SolomonOSKernel(gabriel, graph, context_engine, ai_stack, learning_pipeline)
optimizer = RecursiveOptimizer(solomon_os.dashboard)
# --------------------------------------------------


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    task = {
        "instruction": "chat_response",
        "messages": [{"role": "user", "content": user_message}],
        "required_capability": "chat"
    }

    result = solomon_os.execute_workload(task)
    opt_status = optimizer.evaluate_system_performance()

    return jsonify({
        "reply": result.get("result", ""),
        "system_health": solomon_os.dashboard.get_system_health(),
        "optimization": opt_status
    })

# --- Phase 16 to 20: New API Exposure Endpoints ---

@app.route("/api/gabriel/health", methods=["GET"])
def gabriel_health():
    """Phase 16: Gabriel Health API"""
    return jsonify(solomon_os.dashboard.get_system_health())

@app.route("/api/gabriel/graph", methods=["GET"])
def gabriel_graph():
    """Phase 17: Graph Visualization API"""
    return jsonify({
        "nodes": list(graph.nodes.keys()),
        "edges": graph.edges
    })

@app.route("/api/gabriel/skills", methods=["GET"])
def gabriel_skills():
    """Phase 18: Skill Registry API"""
    return jsonify(skills.skill_registry)

@app.route("/api/gabriel/curiosity", methods=["GET", "POST"])
def gabriel_curiosity():
    """Phase 19: Curiosity Queue API"""
    if request.method == "POST":
        res = curiosity.trigger_autonomous_research()
        return jsonify({"result": res})
    return jsonify(curiosity.research_queue)

@app.route("/api/gabriel/optimize", methods=["POST"])
def gabriel_optimize():
    """Phase 20: Dynamic Optimization Override Endpoint"""
    opt_status = optimizer.evaluate_system_performance()
    return jsonify(opt_status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
