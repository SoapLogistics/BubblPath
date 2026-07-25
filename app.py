import os
import openai
from flask import Flask, request, jsonify
from solomon_abstract_reasoning import FractalOntologySynthesizer

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Instantiate synthesizer globally for API
fractal_synthesizer = FractalOntologySynthesizer()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

@app.route("/api/sple/fractal-ontology/synthesize", methods=["POST"])
def synthesize_cross_domain():
    """
    Exposes Fractal Ontology synthesis capability.
    Requires 'source_concept', 'source_domain', 'target_domain' in payload.
    Also accepts optional 'learn_concepts' array to pre-seed the ontology.
    """
    data = request.json

    # 1. Optionally learn concepts first (useful for testing and dynamic feeding)
    learn_concepts = data.get("learn_concepts", [])
    for lc in learn_concepts:
        fractal_synthesizer.learn_concept(
            concept_name=lc.get("name"),
            domain=lc.get("domain")
        )

    source_concept = data.get("source_concept")
    source_domain = data.get("source_domain")
    target_domain = data.get("target_domain")

    if not all([source_concept, source_domain, target_domain]):
        return jsonify({"error": "Missing required fields: source_concept, source_domain, target_domain"}), 400

    try:
        synthesis = fractal_synthesizer.synthesize_cross_domain_leap(
            source_concept=source_concept,
            source_domain=source_domain,
            target_domain=target_domain
        )
        # Convert tuple back to list for JSON serialization
        synthesis["projected_vector"] = list(synthesis["projected_vector"])
        return jsonify(synthesis), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/sple/fractal-ontology/infinite-learning-cycle", methods=["POST"])
def run_infinite_learning():
    """
    Executes the infinite recursive learning cycle to synthesize and learn new concepts automatically.
    """
    data = request.json or {}
    iterations = data.get("iterations", 1)

    insights = fractal_synthesizer.run_infinite_learning_cycle(iterations=iterations)

    return jsonify({
        "status": "success",
        "iterations": iterations,
        "new_insights_generated": len(insights),
        "insights": insights,
        "total_concepts_in_memory": len(fractal_synthesizer.concepts)
    }), 200

@app.route("/api/sple/fractal-ontology/quantum-collapse", methods=["POST"])
def quantum_collapse():
    """Forces waveform collapse on a quantum superposition concept."""
    data = request.json or {}
    concept_name = data.get("concept_name")

    if not concept_name:
        return jsonify({"error": "Missing concept_name"}), 400

    try:
        domain = fractal_synthesizer.observe_quantum_concept(concept_name)
        return jsonify({
            "status": "success",
            "concept_name": concept_name,
            "collapsed_domain": domain
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/sple/fractal-ontology/holographic-bind", methods=["POST"])
def holographic_bind():
    """Binds multiple concepts into a single HRR interference pattern."""
    data = request.json or {}
    concepts = data.get("concepts", [])

    if not concepts or not isinstance(concepts, list):
        return jsonify({"error": "Provide an array of 'concepts'"}), 400

    try:
        cluster_name, vector = fractal_synthesizer.synthesize_holographic_cluster(concepts)
        return jsonify({
            "status": "success",
            "cluster_name": cluster_name,
            "vector": list(vector) # Return full float projection
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/sple/fractal-ontology/omega-truth", methods=["POST"])
def omega_truth():
    """Calculates the ultimate Omega Truth value of a concept based on the God Node."""
    data = request.json or {}
    concept_name = data.get("concept_name")

    if not concept_name:
        return jsonify({"error": "Missing concept_name"}), 400

    try:
        truth_metrics = fractal_synthesizer.calculate_omega_truth(concept_name)
        return jsonify({
            "status": "success",
            "concept_name": concept_name,
            "metrics": truth_metrics
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
