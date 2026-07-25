import os
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

from solomon_chronos_planner import ChronosTemporalPlanner, Action, StateNode

from solomon_abstract_reasoning import FractalOntologySynthesizer
from solomon_quanta_engine import QuantaEngine
from solomon_nash_swarm import Agent, NashSwarmNegotiator
from solomon_tda import TDAEngine
from solomon_goedel_escape import GoedelEscapeEngine
from solomon_ou_exploration import OUExplorationEngine

# Global instances for the APIs
fractal_synth = FractalOntologySynthesizer()
quanta_engine = QuantaEngine(threshold=0.1)
tda_engine = TDAEngine()
goedel_engine = GoedelEscapeEngine()
ou_engine = OUExplorationEngine()

@app.route("/api/sple/tda/analyze", methods=["POST"])
def tda_analyze():
    data = request.json
    points = [tuple(p) for p in data.get("points", [])]
    epsilon = data.get("epsilon", 1.0)

    topology = tda_engine.analyze_topology(points, epsilon)
    return jsonify({"success": True, "topology": topology})

@app.route("/api/sple/goedel/monitor", methods=["POST"])
def goedel_monitor():
    data = request.json
    state = data.get("state", {})
    triggered, shift = goedel_engine.monitor_state(state)
    return jsonify({
        "success": True,
        "triggered": triggered,
        "paradigm_shift": shift
    })

@app.route("/api/sple/ou-exploration/step", methods=["POST"])
def ou_step():
    data = request.json
    if "reset" in data and data["reset"]:
        ou_engine.reset()
    state = ou_engine.step()
    return jsonify({"success": True, "state": state})

@app.route("/api/chronos/simulate", methods=["POST"])
def chronos_simulate():
    data = request.json
    actions_data = data.get("actions", [])
    start_state = data.get("start_state", {})
    goal_state = data.get("goal_state", {})

    actions = [
        Action(
            a["name"],
            a.get("cost", 1.0),
            a.get("effects", {}),
            a.get("preconditions", {})
        ) for a in actions_data
    ]

    planner = ChronosTemporalPlanner(actions)
    success = planner.execute_plan(start_state, goal_state)

    return jsonify({
        "success": success,
        "final_state": planner.current_node.state if planner.current_node else None,
        "nodes_explored": len(planner.execution_graph)
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
