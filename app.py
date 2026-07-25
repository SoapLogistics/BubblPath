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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
