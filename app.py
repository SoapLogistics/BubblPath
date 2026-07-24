import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for Chrome Extension communication
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    context_data = data.get("context", None)

    # We prepend context if available
    system_prompt = "You are Solomon, a helpful assistant."
    if context_data:
        system_prompt += f" The user is currently looking at {context_data.get('type', 'a webpage')} at {context_data.get('url', '')}. Here is the extracted context: {context_data.get('data', '')}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
        )
        return jsonify({"reply": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route("/api/browser/context", methods=["POST"])
def receive_context():
    data = request.json
    # In a full implementation, we might store this context in a local DB or memory card
    print(f"Received context from {data.get('url')}: {data.get('type')}")
    return jsonify({"status": "Context received successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
