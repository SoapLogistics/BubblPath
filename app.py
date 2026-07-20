import os
import json
import datetime
from flask import Flask, request, jsonify
from openai import OpenAI

from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.extractor.extractor import KnowledgeExtractor
from solomon_knowledge_cards.api.review import ReviewGate
from solomon_knowledge_cards.migrator.importer import DoctrineImporter
from solomon_knowledge_cards.planner.engine import DynamicPlanner
from solomon_knowledge_cards.planner.arbiter import ToolArbiter
from solomon_knowledge_cards.planner.models import TaskPlan

app = Flask(__name__)

# Initialize active database path
DB_FILE = os.environ.get("SOLOMON_DB_PATH", "solomon_cards.db")
db_manager = DatabaseManager(DB_FILE)
repository = CardRepository(db_manager)
extractor = KnowledgeExtractor()
review_gate = ReviewGate(db_manager)
planner = DynamicPlanner(repository)
arbiter = ToolArbiter(repository)

# Safe bootstrap import of legacy checklists on startup
importer = DoctrineImporter(db_manager)
CHECKLISTS_DIR = "openclaw-workspace/checklists/"
if os.path.exists(CHECKLISTS_DIR):
    for f in os.listdir(CHECKLISTS_DIR):
        if f.endswith(".md"):
            full_path = os.path.join(CHECKLISTS_DIR, f)
            card_id = importer.parse_card_id(full_path, "")
            if not db_manager.get_card(card_id, include_deleted=True):
                try:
                    importer.import_file(full_path)
                    print(f"[Bootstrap] Successfully imported legacy checklist: {card_id}")
                except Exception as e:
                    print(f"[Bootstrap] Error importing {full_path}: {e}")

# Global memory storage for active/draft plans since plans can remain in-memory or be saved to extra_metadata
active_plans: dict[str, TaskPlan] = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    clearance = data.get("clearance", "INTERNAL")  # PUBLIC, INTERNAL, RESTRICTED

    memories_str = ""
    if user_message:
        search_results = repository.search(user_message, security_classification=clearance)
        filtered_results = [
            res for res in search_results
            if res["card"]["status"] in ("APPROVED", "ACTIVE")
        ]

        if filtered_results:
            ctx_blocks = []
            for res in filtered_results[:3]:
                card_data = res["card"]
                ctx_blocks.append(
                    f"=== RETRIEVED MEMORY CARD: {card_data['card_id']} ({card_data['card_type']}) ===\n"
                    f"Title: {card_data['title']}\n"
                    f"Summary: {card_data['summary']}\n"
                    f"Body:\n{card_data['body']}\n"
                    f"Problem Solved: {card_data['problem_solved']}\n"
                    f"Why Created: {card_data['why_created']}\n"
                    f"=================================================="
                )
            memories_str = "\n\n".join(ctx_blocks)

    system_prompt = (
        "You are Solomon, a highly capable, self-improving autonomous AI operating system. "
        "Use the retrieved memory cards below (which represent approved legacy operating checklists, "
        "prior failures, and verified remediation playbooks) to inform your reasoning and actions. "
        "Prefer correctness, rigorous governance, and compliance over speed.\n\n"
    )
    if memories_str:
        system_prompt += f"APPROVED OPERATIONAL MEMORY CONTEXT:\n{memories_str}\n\n"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            reply = f"Error querying OpenAI API: {e}"
    else:
        reply = (
            f"[MOCK REPLY - NO API KEY] Received user query: '{user_message}'. "
            f"Retrieved {len(filtered_results) if user_message and 'filtered_results' in locals() else 0} memory blocks."
        )

    return jsonify({
        "reply": reply,
        "context_injected": bool(memories_str)
    })

@app.route("/worker-report", methods=["POST"])
def worker_report():
    """Ingests a Worker Report and generates reviewable draft cards."""
    data = request.json or {}
    report = data.get("report")
    review = data.get("review")

    if not report:
        return jsonify({"error": "Missing 'report' dictionary or markdown string."}), 400

    try:
        draft_cards = extractor.extract_draft_cards(report, review_result=review, creator="extractor")
        for card in draft_cards:
            repository.create_card(card, creator="extractor", reason="Extracted from worker execution endpoint")

        return jsonify({
            "message": f"Successfully extracted and saved {len(draft_cards)} draft cards.",
            "draft_cards": [c.to_dict() for c in draft_cards]
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to extract cards: {e}"}), 500

@app.route("/review", methods=["POST"])
def review_card():
    """Promotes a card through the Review Gate status states."""
    data = request.json or {}
    card_id = data.get("card_id")
    target_status = data.get("target_status")
    updater = data.get("updater", "reviewer")
    reason = data.get("reason")
    notes = data.get("notes")

    if not card_id or not target_status:
        return jsonify({"error": "Missing 'card_id' or 'target_status' parameters."}), 400

    try:
        card = review_gate.transition_status(
            card_id=card_id,
            target_status=target_status,
            updater=updater,
            reason=reason,
            notes=notes
        )
        return jsonify({
            "message": f"Card {card_id} successfully promoted to {target_status}.",
            "card": card.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": f"Review transition failed: {e}"}), 400

@app.route("/cards", methods=["GET"])
def list_cards():
    """Queries, filters, and searches the active memory card store."""
    query = request.args.get("query")
    card_type = request.args.get("card_type")
    tag = request.args.get("tag")
    security = request.args.get("security")

    tags_filter = [tag] if tag else None

    try:
        if query:
            results = repository.search(
                query,
                card_type=card_type,
                tags=tags_filter,
                security_classification=security
            )
            return jsonify({"results": results}), 200
        else:
            cards = repository.list_cards()
            if card_type:
                cards = [c for c in cards if c.card_type.upper() == card_type.upper()]
            if tag:
                cards = [c for c in cards if tag.lower() in [ct.lower() for ct in c.tags]]
            if security:
                cards = [c for c in cards if c.security_classification == security]

            return jsonify({"cards": [c.to_dict() for c in cards]}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list cards: {e}"}), 500

# -------------------------------------------------------------
# Phase 3C: Planning & Safeguards Endpoints
# -------------------------------------------------------------

@app.route("/planner/draft", methods=["POST"])
def draft_task_plan():
    """Formulates a new TaskPlan with pre-emptive safeguards matching the objective."""
    data = request.json or {}
    task_id = data.get("task_id")
    objective = data.get("objective")

    if not task_id or not objective:
        return jsonify({"error": "Missing 'task_id' or 'objective' parameters."}), 400

    try:
        plan = planner.draft_plan(task_id, objective)
        active_plans[plan.plan_id] = plan
        return jsonify({
            "message": "Draft plan formulated successfully.",
            "plan": plan.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"error": f"Plan formulation failed: {e}"}), 500

@app.route("/planner/execute", methods=["POST"])
def execute_task_plan():
    """Simulates plan execution, running tool configuration arbitrations on steps."""
    data = request.json or {}
    plan_id = data.get("plan_id")
    mock_port_config = data.get("port", 3000)
    mock_timeout_config = data.get("timeout_seconds", 30)

    if not plan_id:
        return jsonify({"error": "Missing 'plan_id' parameter."}), 400

    plan = active_plans.get(plan_id)
    if not plan:
        return jsonify({"error": f"Plan {plan_id} not found."}), 404

    execution_history = []

    try:
        # Simulate execution of steps sequentially
        for step in plan.steps:
            action = step["action"]
            tool = step["tool"]

            # Execute Tool arbitration configuration if tool matches
            if tool in ("openhands_run", "bash_run"):
                base_config = {"port": mock_port_config, "timeout_seconds": mock_timeout_config}
                optimized = arbiter.arbitrate_tool_config(action, base_config)

                step_log = {
                    "step_number": step["step_number"],
                    "action": action,
                    "tool": tool,
                    "config_applied": optimized,
                    "status": "COMPLETED"
                }
            else:
                step_log = {
                    "step_number": step["step_number"],
                    "action": action,
                    "tool": tool,
                    "status": "COMPLETED"
                }
            execution_history.append(step_log)

        plan.status = "EXECUTED"
        plan.updated_at = datetime.datetime.now(datetime.UTC).isoformat()

        return jsonify({
            "message": f"Plan {plan_id} successfully executed.",
            "plan_status": plan.status,
            "execution_history": execution_history
        }), 200
    except Exception as e:
        plan.status = "FAILED"
        plan.updated_at = datetime.datetime.now(datetime.UTC).isoformat()
        return jsonify({"error": f"Execution failed: {e}", "plan_status": plan.status}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
