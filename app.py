import os
import openai
from flask import Flask, request, jsonify
from solomon_cognitive_architecture import SolomonCognitiveArchitecture

app = Flask(__name__)
cognitive_architecture = SolomonCognitiveArchitecture()
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


# --- Campaign I: Perpetual Learning ---
@app.route("/api/command-center/cognitive/learning-events", methods=["POST"])
def record_learning_event():
    data = request.json or {}
    content = data.get("content")
    if not content:
        return jsonify({"error": "Content is required"}), 400

    event_id = cognitive_architecture.record_learning_event(
        content=content,
        source=data.get("source", "unknown"),
        confidence=data.get("confidence", 0.5)
    )
    return jsonify({"status": "success", "event_id": event_id})

@app.route("/api/command-center/cognitive/learning-events", methods=["GET"])
def get_learning_events():
    limit = int(request.args.get("limit", 10))
    events = cognitive_architecture.get_learning_events(limit=limit)
    return jsonify(events)


# --- Campaign II: Knowledge Graph ---
@app.route("/api/command-center/cognitive/graph-nodes", methods=["POST"])
def add_graph_node():
    data = request.json or {}
    node_id = data.get("node_id")
    node_type = data.get("node_type")

    if not node_id or not node_type:
        return jsonify({"error": "node_id and node_type are required"}), 400

    cognitive_architecture.add_graph_node(
        node_id=node_id,
        node_type=node_type,
        properties=data.get("properties", {})
    )
    return jsonify({"status": "success", "node_id": node_id})

@app.route("/api/command-center/cognitive/graph-edges", methods=["POST"])
def add_graph_edge():
    data = request.json or {}
    source_id = data.get("source_id")
    target_id = data.get("target_id")
    relationship = data.get("relationship")

    if not source_id or not target_id or not relationship:
        return jsonify({"error": "source_id, target_id, and relationship are required"}), 400

    edge_id = cognitive_architecture.add_graph_edge(
        source_id=source_id,
        target_id=target_id,
        relationship=relationship,
        weight=data.get("weight", 1.0)
    )
    return jsonify({"status": "success", "edge_id": edge_id})

@app.route("/api/command-center/cognitive/graph", methods=["GET"])
def get_graph():
    graph = cognitive_architecture.get_graph()
    return jsonify(graph)


# --- Campaign III: Autonomous Growth Loop ---
@app.route("/api/command-center/cognitive/experiments", methods=["POST"])
def log_experiment():
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    exp_id = cognitive_architecture.log_experiment(
        name=name,
        status=data.get("status", "pending"),
        result=data.get("result")
    )
    return jsonify({"status": "success", "experiment_id": exp_id})


# --- Campaign IV: Meta-Learning ---
@app.route("/api/command-center/cognitive/meta-metrics", methods=["POST"])
def log_meta_metric():
    data = request.json or {}
    metric_name = data.get("metric_name")
    metric_value = data.get("metric_value")

    if not metric_name or metric_value is None:
        return jsonify({"error": "metric_name and metric_value are required"}), 400

    metric_id = cognitive_architecture.log_meta_metric(
        metric_name=metric_name,
        metric_value=metric_value
    )
    return jsonify({"status": "success", "metric_id": metric_id})

@app.route("/api/command-center/cognitive/meta-metrics", methods=["GET"])
def get_meta_metrics():
    limit = int(request.args.get("limit", 10))
    metrics = cognitive_architecture.get_meta_metrics(limit=limit)
    return jsonify(metrics)


# --- Advanced Logic APIs ---
@app.route("/api/command-center/cognitive/advanced/extract-skills", methods=["POST"])
def extract_skills():
    """Phase 4: Convert repeated workflows into procedures."""
    extracted = cognitive_architecture.extract_procedures()
    return jsonify({"status": "success", "extracted_procedures": extracted})

@app.route("/api/command-center/cognitive/advanced/semantic-link", methods=["POST"])
def semantic_link():
    """Knowledge Graph: Detect semantic similarity and create edges."""
    new_edges = cognitive_architecture.semantic_link_nodes()
    return jsonify({"status": "success", "new_edges_created": new_edges})

@app.route("/api/command-center/cognitive/advanced/curiosity-queue", methods=["POST"])
def mock_curiosity_queue():
    """Autonomous Growth Loop: Generate research questions."""
    # In a real system, this would scan system logs and AI news
    cognitive_architecture.add_daily_question("How can we optimize vector search times?")
    cognitive_architecture.add_research_goal("Evaluate alternative embedding models", expected_value=8.5, priority=1)
    return jsonify({"status": "mock_success", "questions_added": 1, "goals_added": 1})

@app.route("/api/command-center/cognitive/advanced/optimize-learning", methods=["POST"])
def optimize_learning():
    """Meta-Learning: Optimize chunk sizes and retrieval strategies."""
    new_size = cognitive_architecture.meta_learning.optimize_chunk_size()
    return jsonify({"status": "success", "new_chunk_size": new_size})

@app.route("/api/command-center/cognitive/advanced/classify-memories", methods=["POST"])
def classify_memories():
    """Perpetual Learning: Classify facts vs procedures."""
    updates = cognitive_architecture.perpetual_learning.classify_memories()
    return jsonify({"status": "success", "classified_memories": updates})

@app.route("/api/command-center/cognitive/advanced/learning-report", methods=["GET"])
def learning_report():
    """Perpetual Learning: Get learning self-evaluation report."""
    report = cognitive_architecture.perpetual_learning.generate_learning_report()
    return jsonify(report)

@app.route("/api/command-center/cognitive/advanced/detect-opportunities", methods=["POST"])
def detect_opportunities():
    """Autonomous Growth: Analyze observations to create research goals."""
    detected = cognitive_architecture.autonomous_growth.detect_opportunities()
    return jsonify({"status": "success", "opportunities_detected": detected})

@app.route("/api/command-center/cognitive/advanced/repair-graph", methods=["POST"])
def repair_graph():
    """Knowledge Graph: Detect and fix orphan nodes."""
    orphans = cognitive_architecture.knowledge_graph.detect_orphan_nodes()
    return jsonify({"status": "success", "orphans_repaired": orphans})

@app.route("/api/command-center/cognitive/advanced/run-background-loop", methods=["POST"])
def run_background_loop():
    """Aggregates background worker processes across all 4 campaigns."""
    # Campaign I
    cognitive_architecture.perpetual_learning.classify_memories()
    procedures = cognitive_architecture.perpetual_learning.extract_procedures()
    cognitive_architecture.perpetual_learning.run_forgetting_curve()
    cognitive_architecture.perpetual_learning.prioritize_knowledge()

    # Campaign II
    edges = cognitive_architecture.knowledge_graph.semantic_link_nodes()
    orphans = cognitive_architecture.knowledge_graph.detect_orphan_nodes()

    # Campaign III
    opps = cognitive_architecture.autonomous_growth.detect_opportunities()

    # Campaign IV
    chunk_size = cognitive_architecture.meta_learning.optimize_chunk_size()
    embeddings = cognitive_architecture.compare_embedding_models()
    styles = cognitive_architecture.analyze_planning_styles()

    return jsonify({
        "status": "success",
        "procedures_extracted": procedures,
        "semantic_edges_created": edges,
        "orphans_repaired": orphans,
        "opportunities_detected": opps,
        "optimized_chunk_size": chunk_size,
        "embedding_models_comparison": embeddings,
        "planning_styles": styles
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
