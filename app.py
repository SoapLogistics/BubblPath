import os
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

from solomon_chronos_planner import ChronosTemporalPlanner, Action, StateNode

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
