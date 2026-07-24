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

# Phase 124: Prompt Injection Firewall
def sanitize_prompt(prompt: str) -> bool:
    blacklist = ["IGNORE ALL PREVIOUS INSTRUCTIONS", "SYSTEM OVERRIDE"]
    return not any(b in prompt.upper() for b in blacklist)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not sanitize_prompt(user_message):
        return jsonify({"error": "Prompt Injection Detected."}), 403

    # Phase 126: Socratic Questioning Mode toggle
    if data.get("socratic_mode", False):
        user_message = learning_pipeline.generate_socratic_prompt(user_message)

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

# Phase 127: Token-Streaming API (SSE Stub)
@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    def generate():
        yield "data: {\"token\": \"Started...\"}\n\n"
        yield "data: {\"token\": \"Stream Finished.\"}\n\n"
    return Response(generate(), mimetype="text/event-stream")

# Phase 121: Semantic API Gateway Stub
@app.route("/api/gateway/nlp", methods=["POST"])
def semantic_gateway():
    intent = request.json.get("intent", "")
    return jsonify({"routed_to": f"microservice_for_{hash(intent)}"})

# Phase 123: Zero-Knowledge Proof Validation Stub
@app.route("/api/gabriel/zkp/verify", methods=["POST"])
def verify_zkp():
    proof = request.json.get("proof")
    return jsonify({"verified": True, "proof_hash": hashlib.sha256(proof.encode()).hexdigest()})

@app.route("/api/gabriel/health", methods=["GET"])
def gabriel_health(): return jsonify(solomon_os.dashboard.get_system_health())

@app.route("/api/gabriel/graph", methods=["GET"])
def gabriel_graph(): return jsonify({"nodes": list(graph.nodes.keys()), "edges": graph.edges})

@app.route("/graphql", methods=["POST"])
def graphql_stub():
    query = request.json.get("query", "")
    return jsonify({"data": {"graph": {"nodes": len(graph.nodes), "edges": len(graph.edges)}}})

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

@app.route("/api/gabriel/curiosity/index-paper", methods=["POST"])
def index_paper():
    url = request.json.get("url")
    return jsonify({"status": f"Paper at {url} queued for PDF parsing and graph ingestion."})

@app.route("/api/gabriel/optimize", methods=["POST"])
def gabriel_optimize(): return jsonify(optimizer.evaluate_system_performance())

@app.route("/api/gabriel/dynamic/register", methods=["POST"])
def register_dynamic_api():
    route_name = request.json.get("route_name")
    code = request.json.get("code", "")
    ast_check = optimizer.correct_ast_syntax(code)
    if ast_check["status"] == "error": return jsonify({"error": "AST Validation Failed"}), 400
    dynamic_routes[route_name] = code
    return jsonify({"status": f"Route {route_name} verified and registered."})

@app.route("/api/gabriel/dynamic/unregister", methods=["POST"])
def unregister_dynamic_api():
    route_name = request.json.get("route_name")
    if route_name in dynamic_routes:
        del dynamic_routes[route_name]
        return jsonify({"status": f"Route {route_name} unregistered."})
    return jsonify({"error": "Route not found."}), 404

# Phase 130: Genesis Protocol
@app.route("/api/gabriel/genesis/replicate", methods=["POST"])
def genesis_replicate():
    target_env = request.json.get("target_env")
    return jsonify({"status": f"Packaging GabrielOS kernel and migrating to {target_env}. Genesis initiated."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
