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

@app.route("/os/proc", methods=["GET"])
def os_proc():
    """Simulates /proc fs, listing detailed runtime information for all loaded modules."""
    proc_info = {}
    for name, module in kernel.modules.items():
        proc_info[name] = module.get_status()
    return jsonify({"proc": proc_info, "total_modules": len(proc_info)})

@app.route("/os/sys/vfs", methods=["GET"])
def vfs_list():
    """Lists files in the Virtual File System."""
    prefix = request.args.get("prefix", "")
    try:
        files = kernel.call_rpc('vfs_list', prefix)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/os/sys/vfs/read", methods=["GET"])
def vfs_read():
    """Reads a file from the Virtual File System."""
    path = request.args.get("path")
    if not path:
        return jsonify({"error": "path parameter is required"}), 400
    try:
        data = kernel.call_rpc('vfs_read', path)
        if data is None:
            return jsonify({"error": "File not found"}), 404
        return jsonify({"path": path, "content": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/os/sys/vfs/write", methods=["POST"])
def vfs_write():
    """Writes JSON data to the Virtual File System."""
    data = request.json
    path = data.get("path")
    content = data.get("content")
    if not path or content is None:
         return jsonify({"error": "path and content are required"}), 400
    try:
        success = kernel.call_rpc('vfs_write', path, content)
        if success:
             return jsonify({"status": "success", "path": path})
        return jsonify({"error": "Write failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
