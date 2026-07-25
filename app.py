import os
import openai
from flask import Flask, request, jsonify

from solomon_core.gabriel.amygdala import AmygdalaRouter
from solomon_fractal_ontology import FractalOntologySynthesizer
from solomon_chronos_planner import ChronosTemporalPlanner
from solomon_clean_room_synthesizer import CleanRoomSynthesizer
from solomon_zero_copy_memory import ZeroCopyMemorySubstrate

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize Subsystems
amygdala_router = AmygdalaRouter()
fractal_synthesizer = FractalOntologySynthesizer()
chronos_planner = ChronosTemporalPlanner()
clean_room = CleanRoomSynthesizer()
zero_copy_mem = ZeroCopyMemorySubstrate()

# Seed Fractal Ontology for demonstration
fractal_synthesizer.add_concept("king", (1.0, 1.0))
fractal_synthesizer.add_concept("man", (1.0, 0.0))
fractal_synthesizer.add_concept("queen", (0.0, 1.0))
fractal_synthesizer.add_concept("woman", (0.0, 0.0))

# Seed Chronos Planner for demonstration
chronos_planner.add_transition("START", "MID1", 1.0, "go_mid1")
chronos_planner.add_transition("MID1", "GOAL", 1.0, "go_goal")
chronos_planner.add_transition("START", "MID2", 1.5, "go_mid2")
chronos_planner.add_transition("MID2", "GOAL", 0.6, "go_goal_alt")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    # Use Amygdala Router for O(1) reflex cache or emotional tagging
    use_cortex, cached_resp, emotional_tags = amygdala_router.route_request(user_message)

    if not use_cortex:
        return jsonify({"reply": cached_resp, "routed_via": "amygdala_reflex"})

    # Append emotional tags to system prompt if any
    system_prompt = "You are Jules Omega Engine (J.O.E.), an extremely skilled AI."
    if emotional_tags:
        system_prompt += f" Consider user emotion context: {emotional_tags}"

    # Generate response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
        )
        reply = response.choices[0].message["content"]

        # Learn for next time
        amygdala_router.learn_response(user_message, reply)

        return jsonify({"reply": reply, "routed_via": "cortex_llm", "emotions_injected": emotional_tags})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sple/fractal-ontology/synthesize", methods=["POST"])
def synthesize_ontology():
    data = request.json
    source_domain = data.get("source_domain", [])
    target_domain = data.get("target_domain", [])
    source_concept = data.get("source_concept", "")

    result = fractal_synthesizer.synthesize_analogical_leap(source_domain, target_domain, source_concept)
    return jsonify({"analogical_leap_result": result})


@app.route("/api/chronos/simulate", methods=["POST"])
def simulate_chronos():
    data = request.json
    start = data.get("start", "START")
    goal = data.get("goal", "GOAL")

    # Retrocausal planning
    plan = chronos_planner.retrocausal_plan(start, goal, lambda x: None)

    return jsonify({"retrocausal_plan": plan})


@app.route("/system/gabriel/invention-lab/simulate", methods=["POST"])
def simulate_invention_lab():
    data = request.json
    operation = data.get("operation", "")

    if operation == "store_memory":
        node_id = data.get("node_id", 1)
        valence = data.get("valence", 0.5)
        arousal = data.get("arousal", 0.5)
        success = zero_copy_mem.store_memory(node_id, valence, arousal)
        return jsonify({"success": success})

    elif operation == "retrieve_memory":
        node_id = data.get("node_id", 1)
        mem = zero_copy_mem.retrieve_memory(node_id)
        return jsonify({"memory": mem})

    elif operation == "heal_function":
        module_name = data.get("module_name", "")
        func_name = data.get("func_name", "")
        new_source = data.get("new_source", "")
        success = clean_room.mutate_and_reload(module_name, func_name, new_source)
        return jsonify({"success": success})

    return jsonify({"error": "Unknown operation"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
