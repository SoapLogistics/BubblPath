import os
import openai
from flask import Flask, request, jsonify, render_template

from hephaestus_forge import hephaestus

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Hephaestus App Forge UI Route
@app.route("/hephaestus", methods=["GET"])
def hephaestus_workspace():
    return render_template("hephaestus_workspace.html")

# Hephaestus App Forge API Endpoints
@app.route("/api/hephaestus/scaffold", methods=["POST"])
def hephaestus_scaffold():
    data = request.json
    app_name = data.get("app_name", "MyAwesomeApp")
    platform = data.get("platform", "cross_platform")
    framework = data.get("framework", "flutter")

    result = hephaestus.scaffold_app(app_name, platform, framework)
    return jsonify(result)

@app.route("/api/hephaestus/compile", methods=["POST"])
def hephaestus_compile():
    data = request.json
    platform = data.get("platform", "cross_platform")
    framework = data.get("framework", "flutter")

    result = hephaestus.compile_instructions(platform, framework)
    return jsonify(result)

@app.route("/api/hephaestus/teach", methods=["POST"])
def hephaestus_teach():
    data = request.json
    topic = data.get("topic")
    content = data.get("content")

    if not topic or not content:
        return jsonify({"error": "Missing topic or content"}), 400

    result = hephaestus.teach_pattern(topic, content)
    return jsonify({"message": result, "knowledge_base": hephaestus.get_knowledge_patterns()})

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
