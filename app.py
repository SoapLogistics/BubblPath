import os
import openai
from flask import Flask, request, jsonify

# SPLE Imports
from solomon_sple_core import Orchestrator
from solomon_meta_learner import MetaLearner
from solomon_curiosity_engine import CuriosityEngine
from solomon_sple_memory import SPLEMemoryManager
from solomon_sple_optimizer import SPLEOptimizer
from solomon_sple_capability import CapabilityAssimilator
from solomon_sple_distributed import DistributedSwarmManager
from solomon_sple_self_eval import SelfEvaluationEngine
from solomon_sple_pat_memory import ProgressiveAbstractionTree

app = Flask(__name__)

# Initialize SPLE Subsystems
sple_orchestrator = Orchestrator()
sple_meta_learner = MetaLearner()
sple_curiosity = CuriosityEngine()
sple_memory = SPLEMemoryManager()
sple_optimizer = SPLEOptimizer()
sple_capability = CapabilityAssimilator()
sple_swarm = DistributedSwarmManager()
sple_self_eval = SelfEvaluationEngine()
sple_pat_memory = ProgressiveAbstractionTree()

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

# ==========================================
# SPLE (Solomon Perpetual Learning Engine) Endpoints
# ==========================================

@app.route("/api/sple/status", methods=["GET"])
def sple_status():
    """Returns the current status of the SPLE orchestrator and subsystems."""
    return jsonify({
        "orchestrator_running": sple_orchestrator.is_running,
        "queue_depth": len(sple_orchestrator.task_queue),
        "memory_stats": {
            "episodic_count": len(sple_memory.episodic_memory),
            "semantic_nodes": len(sple_memory.semantic_memory)
        },
        "optimizer_metrics": sple_optimizer.global_metrics,
        "swarm_nodes": len(sple_swarm.nodes)
    })

@app.route("/api/sple/enqueue", methods=["POST"])
def sple_enqueue():
    """Enqueues a task for the SPLE orchestrator to process."""
    data = request.json
    task_type = data.get("type", "generic")
    payload = data.get("payload", {})
    sple_orchestrator.enqueue_task(task_type, payload)

    # Store in episodic memory
    sple_memory.store_episodic({"type": "task_enqueued", "task_type": task_type})

    return jsonify({"status": "Task enqueued", "queue_depth": len(sple_orchestrator.task_queue)})

@app.route("/api/sple/trigger-sleep", methods=["POST"])
def sple_trigger_sleep():
    """Manually triggers the memory sleep consolidation cycle."""
    result = sple_memory.trigger_sleep_consolidation()
    return jsonify(result)

@app.route("/api/sple/optimize", methods=["POST"])
def sple_optimize():
    """Manually triggers the global optimizer cycle."""
    result = sple_optimizer.run_optimization_cycle()
    return jsonify(result)

@app.route("/api/sple/delegate", methods=["POST"])
def sple_delegate():
    """Delegates a task to the distributed swarm."""
    data = request.json
    task = data.get("task", "Analyze code structure")
    role = data.get("role", "Coder")
    result = sple_swarm.delegate_task(task, role)
    return jsonify(result)

@app.route("/api/sple/evaluate", methods=["POST"])
def sple_evaluate():
    """Triggers the adversarial Self-Evaluation engine."""
    data = request.json
    target_code = data.get("code", "def default(): pass")
    result = sple_self_eval.red_team_adversarial_review(target_code)
    return jsonify(result)

@app.route("/api/sple/memory/abstract", methods=["POST"])
def sple_memory_abstract():
    """Simulates abstracting facts into a Progressive Abstraction Tree."""
    data = request.json
    facts = data.get("facts", ["The sky is blue", "Water is wet"])
    concept = data.get("concept", "Basic Natural Truths")

    fact_ids = [sple_pat_memory.ingest_raw_fact(f) for f in facts]
    parent_id = sple_pat_memory.abstract_cluster(fact_ids, concept)

    return jsonify({
        "status": "success",
        "abstracted_node_id": parent_id,
        "worldview_size": len(sple_pat_memory.root_nodes)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
