import time
import os
import json
from functools import wraps
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.extractor.extractor import KnowledgeExtractor
from solomon_knowledge_cards.api.review import ReviewGate
from solomon_knowledge_cards.storage.queue import TaskQueue

from solomon_knowledge_cards.migrator.importer import DoctrineImporter

# Initialize Flask app
app = Flask(__name__)

# Use a stable absolute path for the SQLite database
DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "solomon_mnemosyne.db"))
DB_PATH = os.environ.get("SOLOMON_DB_PATH", DEFAULT_DB_PATH)

db_manager = DatabaseManager(DB_PATH)
repository = CardRepository(db_manager)
extractor = KnowledgeExtractor()
review_gate = ReviewGate(db_manager)
task_queue = TaskQueue(DB_PATH)

# Global execution state for the kill switch
SYSTEM_STATE = "ACTIVE"  # Can be ACTIVE or PAUSED_BLOCKED


# OpenAI Client (Modern library support)
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None
DEFAULT_MODEL = os.environ.get("SOLOMON_MODEL", "gpt-3.5-turbo")

# Run Doctrine Importer on startup to load standard operational checklists
# Rather than checking if the DB is empty, check whether each file has already been imported
try:
    importer = DoctrineImporter(db_manager)
    checklists_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "openclaw-workspace", "checklists"))
    if os.path.exists(checklists_dir):
        # Gather all currently registered legacy doctrine sources
        all_cards = repository.list_cards()
        registered_sources = set()
        for card in all_cards:
            for source in card.source_ids:
                registered_sources.add(os.path.abspath(source))

        # Scan for md files in the checklists folder and import only missing ones
        for file in os.listdir(checklists_dir):
            if file.endswith(".md"):
                full_path = os.path.abspath(os.path.join(checklists_dir, file))
                if full_path not in registered_sources:
                    importer.import_file(full_path)
                    print(f"Doctrine Importer successfully imported checklist: {file}")
except Exception as e:
    print(f"Warning: Doctrine Importer failed during startup: {e}")


# Auth Decorator
API_BEARER_TOKEN = os.environ.get("SOLOMON_API_TOKEN", "solomon-dev-token-99")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized. Missing or invalid Bearer token."}), 401

        token = auth_header.split(" ")[1]
        if token != API_BEARER_TOKEN:
            return jsonify({"error": "Forbidden. Invalid token."}), 403

        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET"])
def index():
    """
    Renders the modern Solomon Cognitive Workspace WebUI dashboard.
    """
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
@require_auth
def chat():
    data = request.json or {}
    user_message = data.get("message", "")

    # Enforce hierarchical security classification clearance (default: INTERNAL)
    # Clearance Levels: PUBLIC (1) -> INTERNAL (2) -> RESTRICTED (3)
    user_clearance_str = str(data.get("security_classification", "INTERNAL")).upper()
    clearance_levels = {"PUBLIC": 1, "INTERNAL": 2, "RESTRICTED": 3}
    user_clearance = clearance_levels.get(user_clearance_str, 2)

    # 1. Retrieve prior ACTIVE or APPROVED cards from the repository
    retrieved_context = ""
    try:
        search_results = repository.search(user_message)
        # Filter for ACTIVE/APPROVED status and ensure security classification is within user's clearance level
        filtered_results = []
        for res in search_results:
            card = res["card"]
            if card["status"] in ("ACTIVE", "APPROVED"):
                card_sec_str = card.get("security_classification", "INTERNAL").upper()
                card_sec_level = clearance_levels.get(card_sec_str, 2)
                if card_sec_level <= user_clearance:
                    filtered_results.append(res)

        if filtered_results:
            context_blocks = []
            for item in filtered_results[:3]: # Retrieve top 3 relevant cards
                card = item["card"]
                block = (
                    f"--- MEMORY CARD {card['card_id']} ({card['card_type']}) ---\n"
                    f"Title: {card['title']}\n"
                    f"Summary: {card['summary']}\n"
                    f"Why Created: {card['why_created']}\n"
                    f"Problem Solved: {card['problem_solved']}\n"
                    f"Body:\n{card['body']}\n"
                )
                context_blocks.append(block)
            retrieved_context = "\n".join(context_blocks)
    except Exception as e:
        print(f"Error during memory retrieval: {e}")

    # 2. Inject context into the LLM system prompt before generating the reply
    system_instruction = (
        "You are Solomon, an extremely capable cognitive AI assistant.\n"
        "You possess a memory system filled with structured Knowledge Cards. Use the following context "
        "retrieved from your memory repository to inform your responses, plan tasks, or troubleshoot failures.\n"
    )
    if retrieved_context:
        system_instruction += (
            f"\nRelevant Retrieved Memory Context:\n"
            f"{retrieved_context}\n"
            f"End of Retrieved Memory Context.\n"
        )
    else:
        system_instruction += "\nNo relevant memory context retrieved.\n"

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_message}
    ]

    try:
        if client:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
            )
            reply = response.choices[0].message.content
        else:
            reply = "Warning: OpenAI API Key not configured. Prompt would have been processed."
    except Exception as e:
        reply = f"Error calling OpenAI API: {e}"

    return jsonify({
        "reply": reply,
        "retrieved_context": retrieved_context
    })


@app.route("/worker-report", methods=["POST"])
@require_auth
def worker_report():
    """
    Ingest a worker report (JSON or Markdown) and optional review result.
    Processes them, saves the generated candidate cards in DRAFT state,
    and returns metadata of generated cards.
    """
    data = request.json or {}
    report = data.get("report")
    review = data.get("review")

    if not report:
        return jsonify({"error": "Missing 'report' parameter."}), 400

    try:
        draft_cards = extractor.extract_draft_cards(report, review, creator="runtime_extractor")
        response_cards = []
        for card in draft_cards:
            repository.create_card(card, creator="runtime_extractor", reason="Ingested via /worker-report endpoint")
            response_cards.append({
                "card_id": card.card_id,
                "card_type": card.card_type,
                "title": card.title,
                "status": card.status,
                "validation_state": card.validation_state
            })
        return jsonify({
            "success": True,
            "message": f"Successfully processed report. Generated {len(response_cards)} candidate cards.",
            "cards": response_cards
        })
    except Exception as e:
        return jsonify({"error": f"Failed to extract cards from report: {e}"}), 500


@app.route("/review", methods=["POST"])
@require_auth
def review_card():
    """
    Submit an SS3 review or promotion request for a draft card.
    Expected payload:
    {
        "card_id": "FC-XXXXXX",
        "action": "approve" | "activate" | "review" | "reject",
        "notes": "review notes" (optional),
        "reason": "transition reason" (optional)
    }
    """
    data = request.json or {}
    card_id = data.get("card_id")
    action = data.get("action")
    notes = data.get("notes")
    reason = data.get("reason")

    if not card_id or not action:
        return jsonify({"error": "Missing 'card_id' or 'action' parameter."}), 400

    action = action.lower()
    try:
        if action == "review":
            if not notes:
                return jsonify({"error": "Notes are required for 'review' action"}), 400
            updated_card = review_gate.review_card(card_id, notes=notes, updater="runtime_reviewer")
        elif action == "approve":
            updated_card = review_gate.approve_card(card_id, updater="runtime_approver")
        elif action == "activate":
            updated_card = review_gate.activate_card(card_id, updater="runtime_operator")
        elif action == "reject":
            if not reason:
                return jsonify({"error": "Reason is required for 'reject' action"}), 400
            updated_card = review_gate.reject_card(card_id, reason=reason, updater="runtime_reviewer")
        else:
            return jsonify({"error": f"Unsupported action: '{action}'."}), 400

        return jsonify({
            "success": True,
            "card_id": updated_card.card_id,
            "status": updated_card.status,
            "validation_state": updated_card.validation_state
        })
    except Exception as e:
        return jsonify({"error": f"Failed to transition status for card {card_id}: {e}"}), 500


@app.route("/cards", methods=["GET"])
@require_auth
def list_or_search_cards():
    """
    Lists all cards or searches with keyword filtering.
    Query parameters:
    - query: string
    - type: card type
    - tag: tag name
    """
    query = request.args.get("query")
    card_type = request.args.get("type")
    tag = request.args.get("tag")

    tags = [tag] if tag else None

    try:
        if query or card_type or tags:
            results = repository.search(query=query, card_type=card_type, tags=tags)
            serialized = results
        else:
            all_cards = repository.list_cards()
            serialized = [c.to_dict() for c in all_cards]
        return jsonify({
            "success": True,
            "count": len(serialized),
            "results": serialized
        })
    except Exception as e:
        return jsonify({"error": f"Failed to list/search cards: {e}"}), 500



@app.route("/queue/enqueue", methods=["POST"])
@require_auth
def enqueue_task():
    if SYSTEM_STATE == "PAUSED_BLOCKED":
        return jsonify({"error": "System is currently PAUSED_BLOCKED. No new tasks accepted."}), 503

    data = request.json or {}
    task_type = data.get("task_type")
    payload = data.get("payload", {})

    if not task_type:
        return jsonify({"error": "Missing 'task_type'"}), 400

    try:
        task_id = task_queue.enqueue(task_type, payload)
        return jsonify({"success": True, "task_id": task_id, "status": "PENDING"})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500

@app.route("/queue/dequeue", methods=["GET"])
@require_auth
def dequeue_task():
    if SYSTEM_STATE == "PAUSED_BLOCKED":
        return jsonify({"message": "System is paused. No tasks distributed."}), 503

    try:
        task = task_queue.dequeue()
        if not task:
            return jsonify({"message": "Queue empty."}), 404
        return jsonify({"success": True, "task": task})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500

@app.route("/system/kill", methods=["POST"])
@require_auth
def kill_switch():
    global SYSTEM_STATE
    SYSTEM_STATE = "PAUSED_BLOCKED"
    return jsonify({"success": True, "message": "EMERGENCY STOP ENGAGED. System transitioned to PAUSED_BLOCKED."})

@app.route("/system/resume", methods=["POST"])
@require_auth
def resume_switch():
    global SYSTEM_STATE
    SYSTEM_STATE = "ACTIVE"
    return jsonify({"success": True, "message": "System resumed to ACTIVE."})


@app.route("/heartbeat", methods=["POST"])
@require_auth
def heartbeat():
    if SYSTEM_STATE == "PAUSED_BLOCKED":
        return jsonify({"status": "PAUSED_BLOCKED"}), 503
    return jsonify({"status": "OK"})


@app.route("/metrics", methods=["GET"])
@require_auth
def metrics():
    try:
        # Get count of all cards and active cards
        all_cards = repository.list_cards(include_deleted=False)
        active_cards = [c for c in all_cards if c.status == "ACTIVE"]

        # Calculate rolling average confidence
        total_confidence = sum(c.confidence for c in all_cards)
        avg_confidence = total_confidence / len(all_cards) if all_cards else 0.0

        # Check queue
        with db_manager._lock:
            conn = db_manager._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM task_queue WHERE status = 'PENDING'")
                pending_tasks = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM task_queue WHERE status = 'COMPLETED'")
                completed_tasks = cursor.fetchone()[0]
            finally:
                conn.close()

        # Uptime emulation (assuming deployment on linux container/systemd, we check the process age, but for now we mock start time)
        import psutil
        p = psutil.Process(os.getpid())
        uptime_seconds = time.time() - p.create_time()

        return jsonify({
            "success": True,
            "status": SYSTEM_STATE,
            "system": {
                "uptime_seconds": uptime_seconds,
                "process_memory_mb": p.memory_info().rss / 1024 / 1024
            },
            "knowledge_cards": {
                "total_cards": len(all_cards),
                "active_cards": len(active_cards),
                "average_confidence": round(avg_confidence, 3)
            },
            "queue": {
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to gather metrics: {e}"}), 500


@app.route("/system/reflect", methods=["POST"])
@require_auth
def autonomous_reflection():
    if SYSTEM_STATE == "PAUSED_BLOCKED":
        return jsonify({"status": "PAUSED_BLOCKED"}), 503

    try:
        # Simulate autonomous reflection over vector embeddings
        # In a full system, this would cluster embeddings via K-Means and find duplicate/contradictory records.
        all_cards = repository.list_cards()

        # Super simple mock reflection finding
        if len(all_cards) > 50:
            draft_lesson = {
                "card_type": "LESSON",
                "title": "Automated Reflection: High volume of general Knowledge Cards",
                "summary": "Repository is scaling, consider deprecating older duplicates.",
                "body": "Detected > 50 cards in repo. Running maintenance suggestions.",
            }
            # Enqueue a task for an active worker to actually resolve
            task_queue.enqueue("REFLECT_COMPRESS", {"finding": draft_lesson})
            return jsonify({"success": True, "message": "Reflection complete. Maintenance task queued."})

        return jsonify({"success": True, "message": "Reflection complete. No anomalies detected."})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500


@app.route("/system/mutate", methods=["POST"])
@require_auth
def mutate_procedure():
    if SYSTEM_STATE == "PAUSED_BLOCKED":
        return jsonify({"status": "PAUSED_BLOCKED"}), 503

    data = request.json or {}
    repair_card_id = data.get("repair_card_id")

    if not repair_card_id:
        return jsonify({"error": "Missing 'repair_card_id'"}), 400

    try:
        # Enqueue a high-priority task for OpenHands/Codex to create a git branch and alter Markdown
        task_id = task_queue.enqueue("MUTATE_PROCEDURE_MARKDOWN", {
            "repair_card_id": repair_card_id,
            "instruction": "Open the original markdown file specified in this repair card and inject the remediation steps."
        })
        return jsonify({
            "success": True,
            "message": f"Procedure mutation queued. Worker will open PR/Branch based on repair {repair_card_id}",
            "task_id": task_id
        })
    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500


@app.route("/system/mcp/start", methods=["POST"])
@require_auth
def start_mcp_server():
    if SYSTEM_STATE == "PAUSED_BLOCKED":
        return jsonify({"status": "PAUSED_BLOCKED"}), 503

    data = request.json or {}
    server_name = data.get("server_name")

    if not server_name:
        return jsonify({"error": "Missing 'server_name'"}), 400

    try:
        # Simulate local MCP Subprocess spinup logic
        # e.g., subprocess.Popen(["npx", "-y", "@modelcontextprotocol/server-postgres", "postgresql://..."])
        task_id = task_queue.enqueue("SPINUP_MCP_SERVER", {
            "server_name": server_name,
            "config": data.get("config", {})
        })
        return jsonify({
            "success": True,
            "message": f"MCP Spinup request queued for {server_name}.",
            "task_id": task_id
        })
    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
