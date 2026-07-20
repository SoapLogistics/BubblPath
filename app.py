import os
import openai
import datetime
from flask import Flask, request, jsonify
from solomon_knowledge_cards.models import KnowledgeCardModel, CardType, CardStatus, ValidationState
from solomon_knowledge_cards.db import SQLiteDatabase
from solomon_knowledge_cards.repository import KnowledgeRepository
from solomon_knowledge_cards.engine import KnowledgeEngine
from solomon_knowledge_cards.importer import DoctrineImporter

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 1. Initialize SOK Core persistence and engine
db_path = os.environ.get("SOLOMON_DB_PATH", "solomon_cards.db")
db = SQLiteDatabase(db_path)
repo = KnowledgeRepository(db)
engine = KnowledgeEngine(repo)

# 2. Ingest existing procedural legacy checklists on startup
workspace_checklists_dir = os.environ.get("WORKSPACE_CHECKLISTS_DIR", "openclaw-workspace/checklists/")
if os.path.exists(workspace_checklists_dir):
    importer = DoctrineImporter(repo)
    importer.batch_import_directory(workspace_checklists_dir)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return jsonify({"reply": response.choices[0].message["content"]})

# SOK Endpoint: Get Status & Metrics
@app.route("/api/command-center/status", methods=["GET"])
def get_sok_status():
    metrics = engine.calculate_sok_metrics(export_path=None)
    maintenance_res = engine.run_passive_growth_maintenance()
    return jsonify({
        "status": "HEALTHY",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "sok_metrics": metrics,
        "maintenance_cleanup_run": maintenance_res
    })

# SOK Endpoint: Create or Retrieve Cards
@app.route("/api/command-center/cards", methods=["GET", "POST"])
def handle_sok_cards():
    if request.method == "GET":
        query = request.args.get("query")
        card_type = request.args.get("type")
        tag = request.args.get("tag")

        if query:
            cards = repo.search_by_text(query)
        elif card_type:
            cards = repo.search_by_type(card_type)
        elif tag:
            cards = repo.search_by_tags([tag])
        else:
            cards = repo.list_cards()

        return jsonify([c.to_dict() for c in cards])

    elif request.method == "POST":
        data = request.json or {}
        try:
            card = KnowledgeCardModel.from_dict(data)
            repo.update_card(card, actor="API_GATEWAY")
            return jsonify({"status": "SUCCESS", "card": card.to_dict()}), 201
        except Exception as e:
            return jsonify({"status": "ERROR", "reason": str(e)}), 400

# SOK Endpoint: Submit Worker Report
@app.route("/api/command-center/worker-report", methods=["POST"])
def post_worker_report():
    data = request.json or {}
    try:
        extracted = engine.extract_from_report(data)
        return jsonify({
            "status": "SUCCESS",
            "message": f"Successfully processed report, generated {len(extracted)} draft cards.",
            "draft_cards": [c.to_dict() for c in extracted]
        }), 201
    except Exception as e:
        return jsonify({"status": "ERROR", "reason": str(e)}), 400

# SOK Endpoint: Review Draft Cards (Promotion Gate / Rejection Gate)
@app.route("/api/command-center/review", methods=["POST"])
def review_draft_card():
    data = request.json or {}
    card_id = data.get("card_id")
    action = data.get("action")  # "APPROVE" or "REJECT"
    reason = data.get("reason", "API manual review action.")
    reviewer = data.get("reviewer", "SS3")

    if not card_id or not action:
        return jsonify({"status": "ERROR", "reason": "Missing required card_id or action parameter."}), 400

    try:
        if action == "APPROVE":
            engine.promote_card(card_id, reviewer=reviewer)
        elif action == "REJECT":
            engine.reject_card(card_id, reason=reason, reviewer=reviewer)
        else:
            return jsonify({"status": "ERROR", "reason": f"Unsupported review action: {action}"}), 400

        updated_card = repo.get_card(card_id)
        return jsonify({
            "status": "SUCCESS",
            "card_id": card_id,
            "card_status": updated_card.status if updated_card else "DELETED"
        })
    except Exception as e:
        return jsonify({"status": "ERROR", "reason": str(e)}), 400

# SOK Endpoint: Solomon Chat with Automated Memory Context Injection
@app.route("/api/command-center/solomon-chat", methods=["POST"])
def post_solomon_chat():
    data = request.json or {}
    user_message = data.get("message", "")

    # Pre-task recall search
    prior_guidance = engine.retrieve_active_operational_guidance(user_message)

    # Inject context
    system_prompt = (
        "You are Solomon, a highly capable self-improving cognitive operating core.\n"
        "Enforce SOK safe protocols. Incorporate the following trusted active memory cards into your context:\n"
    )
    if prior_guidance:
        for idx, result in enumerate(prior_guidance, 1):
            system_prompt += f"Memory Card {idx}:\n- Title: {result['title']}\n- Type: {result['type']}\n- Guidance: {result['evidence']}\n"
    else:
        system_prompt += "No relevant memory cards matched this task context.\n"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return jsonify({
            "reply": response.choices[0].message["content"],
            "injected_memory_context": prior_guidance
        })
    except Exception as e:
        return jsonify({"status": "ERROR", "reason": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
