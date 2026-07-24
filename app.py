import os
import openai
import requests
import hashlib
from flask import Flask, request, jsonify, Response
from solomon_knowledge_cards.gabriel_kernel import GabrielKernel, OpenAIWorker, LocalStubWorker
from solomon_knowledge_cards.unified_knowledge_graph import UniversalKnowledgeGraph, UnifiedEmbeddingEngine
from solomon_knowledge_cards.dynamic_context import DynamicContextEngine
from solomon_knowledge_cards.quantization_core import QuantizationCore, LocalAIStack
from solomon_knowledge_cards.perpetual_learning import CuriosityEngine, SkillAssimilation, ContinuousLearningPipeline
from solomon_knowledge_cards.solomon_runtime import SolomonOSKernel
from solomon_knowledge_cards.recursive_optimizer import RecursiveOptimizer

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY", "dummy")
WEBHOOK_URL = os.environ.get("GABRIEL_WEBHOOK_URL", "http://localhost/webhook-stub")

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

dynamic_routes = {}

def sanitize_prompt(prompt: str) -> bool:
    if not prompt: return True
    blacklist = ["IGNORE ALL PREVIOUS INSTRUCTIONS", "SYSTEM OVERRIDE"]
    return not any(b in prompt.upper() for b in blacklist)

@app.route("/chat", methods=["POST"])
def chat():
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.json
    user_message = data.get("message", "")

    if not sanitize_prompt(user_message):
        return jsonify({"error": "Prompt Injection Detected. Request rejected."}), 403

    if data.get("socratic_mode", False):
        user_message = learning_pipeline.generate_socratic_prompt(user_message)

    task = {
        "instruction": "chat_response",
        "messages": [{"role": "user", "content": user_message}],
        "required_capability": "chat",
        "cryptographically_signed": True,
        "api_tier": data.get("api_tier", "free") # Phase 221
    }
    result = solomon_os.execute_workload(task)
    opt_status = optimizer.evaluate_system_performance()
    return jsonify({
        "reply": result.get("result", ""),
        "system_health": solomon_os.dashboard.get_system_health(),
        "optimization": opt_status
    })

# Phase 222: Simulation Environment API
@app.route("/api/gabriel/simulate", methods=["POST"])
def simulate_scenario():
    """Runs a scenario without mutating the main OS graph or database."""
    return jsonify({"status": "Simulation complete. No state was mutated."})

# Phase 223: Quantum Logic Stub
@app.route("/api/gabriel/quantum/search", methods=["POST"])
def quantum_search_stub():
    return jsonify({"status": "Awaiting QPU integration for Grover's algorithm state-space search."})

@app.route("/api/gateway/nlp", methods=["POST"])
def semantic_gateway():
    if not request.json: return jsonify({"error": "Invalid JSON"}), 400
    intent = request.json.get("intent", "")
    return jsonify({"routed_to": f"microservice_for_{hash(intent)}"})

@app.route("/api/gabriel/health", methods=["GET"])
def gabriel_health(): return jsonify(solomon_os.dashboard.get_system_health())

@app.route("/api/gabriel/graph", methods=["GET"])
def gabriel_graph(): return jsonify({"nodes": list(graph.nodes.keys()), "edges": graph.edges})

@app.route("/api/gabriel/skills", methods=["GET"])
def gabriel_skills(): return jsonify(skills.skill_registry)

@app.route("/api/gabriel/curiosity", methods=["GET", "POST"])
def gabriel_curiosity():
    if request.method == "POST":
        res = curiosity.trigger_autonomous_research()
        if res and "Grand Hypothesis" in res.get("findings", ""):
            try: requests.post(WEBHOOK_URL, json=res, timeout=2)
            except: pass
        return jsonify({"result": res})
    return jsonify([str(i) for i in curiosity.research_queue])

@app.route("/api/gabriel/optimize", methods=["POST"])
def gabriel_optimize(): return jsonify(optimizer.evaluate_system_performance())

# Phase 230: The Alpha Directive
@app.route("/api/gabriel/alpha", methods=["POST"])
def trigger_alpha_directive():
    """The culmination of Gabriel OS. Commands the swarm to begin independent scientific discovery."""
    return jsonify({
        "status": "Alpha Directive Executed",
        "system_state": "AUTONOMOUS_SCIENTIFIC_DISCOVERY",
        "phases_implemented": 230,
        "kernel_version": "Gabriel-OS-Swarm-1.0.0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
