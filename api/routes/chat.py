import os
import openai
from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})
