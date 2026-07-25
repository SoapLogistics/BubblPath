import os
import openai
from flask import Flask, request, jsonify
from solomon_core.gabriel.amygdala import AmygdalaRouter

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

import threading
import time

# Initialize the global Amygdala Router
amygdala = AmygdalaRouter()

def start_dream_cycle():
    """
    Background daemon thread to periodically consolidate and prune memories.
    Runs every 60 seconds. In a true production 20-year system, this might run
    nightly, but for fast iteration/efficiency, we run it frequently.
    """
    def _dream_loop():
        while True:
            try:
                # We use sleep so the thread doesn't hog the CPU
                time.sleep(60)
                pruned = amygdala.dream_consolidation(max_capacity=5000, max_age_seconds=3600)
                if pruned > 0:
                    print(f"[DREAM CYCLE] Pruned {pruned} weak/old synapses from reflex arc.")
            except Exception as e:
                # Ensure the background thread never dies from an uncaught exception
                print(f"[DREAM CYCLE] Error during consolidation: {e}")

    dream_thread = threading.Thread(target=_dream_loop, daemon=True)
    dream_thread.start()

# Start the dream cycle when the app starts
start_dream_cycle()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    # 1. Amygdala Routing Protocol (Reflex Check)
    routing_decision = amygdala.process(user_message)

    if routing_decision["route"] == "reflex":
        # Bypass the LLM entirely (Neural Efficiency)
        return jsonify({
            "reply": routing_decision["response"],
            "route": "reflex",
            "tags": routing_decision["tags"],
            "metrics": routing_decision["metrics"]
        })

    # 2. Cortex Wake-up (LLM Call)
    # Inject the emotional tags as a system prompt hint
    tags = routing_decision["tags"]
    system_prompt = (
        f"You are the Cortex. The Amygdala detected: "
        f"Urgency={tags['urgency']:.2f}, Frustration={tags['frustration']:.2f}, "
        f"Complexity={tags['complexity']:.2f}. "
        f"Adjust your tone and verbosity accordingly."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
    )
    reply_content = response.choices[0].message["content"]

    # 3. Myelination (Learning)
    # Store the response in the reflex arc for next time if complexity is low
    learned = amygdala.learn(user_message, reply_content)

    return jsonify({
        "reply": reply_content,
        "route": "cortex",
        "tags": tags,
        "learned_as_reflex": learned
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
