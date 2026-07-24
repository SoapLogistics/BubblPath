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

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    task = {
        "instruction": "chat_response",
        "messages": [{"role": "user", "content": data.get("message", "")}],
        "required_capability": "chat"
    }
    result = solomon_os.execute_workload(task)
    opt_status = optimizer.evaluate_system_performance()
    return jsonify({
        "reply": result.get("result", ""),
        "system_health": solomon_os.dashboard.get_system_health(),
        "optimization": opt_status
    })

@app.route("/api/gabriel/health", methods=["GET"])
def gabriel_health():
    return jsonify(solomon_os.dashboard.get_system_health())

@app.route("/api/gabriel/graph", methods=["GET"])
def gabriel_graph():
    return jsonify({"nodes": list(graph.nodes.keys()), "edges": graph.edges})

@app.route("/api/gabriel/skills", methods=["GET"])
def gabriel_skills():
    return jsonify(skills.skill_registry)

@app.route("/api/gabriel/curiosity", methods=["GET", "POST"])
def gabriel_curiosity():
    if request.method == "POST":
        res = curiosity.trigger_autonomous_research()
        return jsonify({"result": res})
    # Cannot serialize priority queue easily, return string format
    return jsonify([str(i) for i in curiosity.research_queue])

@app.route("/api/gabriel/optimize", methods=["POST"])
def gabriel_optimize():
    return jsonify(optimizer.evaluate_system_performance())

# Phase 27 & 30: Dynamic APIs & Federated Sync Hooks
@app.route("/api/gabriel/dynamic/register", methods=["POST"])
def register_dynamic_api():
    return jsonify({"status": "API registered in memory."})

@app.route("/api/gabriel/federated/sync", methods=["POST"])
def federated_sync():
    data = request.json
    graph.ingest_federated_graph(data.get("nodes", {}), data.get("edges", {}))
    return jsonify({"status": "Federated graph synced."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
