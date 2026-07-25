import os
import openai
from flask import Flask, request, jsonify
from solomon_os.kernel import kernel
from solomon_os.modules.memory import MemoryModule
from solomon_os.modules.planning import PlanningModule
from solomon_os.modules.workers import WorkersModule
from solomon_os.modules.browser import BrowserModule
from solomon_os.modules.vision import VisionModule
from solomon_os.modules.voice import VoiceModule
from solomon_os.modules.scheduling import SchedulingModule
from solomon_os.modules.learning import LearningModule
from solomon_os.modules.security import SecurityModule
from solomon_os.modules.networking import NetworkingModule
from solomon_os.modules.storage import StorageModule
from solomon_os.modules.ai_models import AIModelsModule
from solomon_os.modules.tool_routing import ToolRoutingModule

app = Flask(__name__)

# --- Solomon OS Kernel Boot Sequence ---
kernel.boot()
kernel.load_module(StorageModule())
kernel.load_module(NetworkingModule())
kernel.load_module(SecurityModule())
kernel.load_module(MemoryModule())
kernel.load_module(AIModelsModule())
kernel.load_module(VisionModule())
kernel.load_module(VoiceModule())
kernel.load_module(BrowserModule())
kernel.load_module(ToolRoutingModule())
kernel.load_module(WorkersModule())
kernel.load_module(PlanningModule())
kernel.load_module(LearningModule())
kernel.load_module(SchedulingModule())
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/os/status", methods=["GET"])
def os_status():
    return jsonify(kernel.get_system_status())

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
