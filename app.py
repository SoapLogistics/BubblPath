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

app = Flask(__name__)

# Initialize active database path
DB_FILE = os.environ.get("SOLOMON_DB_PATH", "solomon_cards.db")
db_manager = DatabaseManager(DB_FILE)
repository = CardRepository(db_manager)
extractor = KnowledgeExtractor()
review_gate = ReviewGate(db_manager)

# Safe bootstrap import of legacy checklists on startup
importer = DoctrineImporter(db_manager)
CHECKLISTS_DIR = "openclaw-workspace/checklists/"
if os.path.exists(CHECKLISTS_DIR):
    for f in os.listdir(CHECKLISTS_DIR):
        if f.endswith(".md"):
            full_path = os.path.join(CHECKLISTS_DIR, f)
            card_id = importer.parse_card_id(full_path, "")
            # Verify if already imported to prevent duplicate operations
            if not db_manager.get_card(card_id, include_deleted=True):
                try:
                    importer.import_file(full_path)
                    print(f"[Bootstrap] Successfully imported legacy checklist: {card_id}")
                except Exception as e:
                    print(f"[Bootstrap] Error importing {full_path}: {e}")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    clearance = data.get("clearance", "INTERNAL")  # PUBLIC, INTERNAL, RESTRICTED

    # 1. Retrieve related approved operational guidance
    memories_str = ""
    if user_message:
        # Search approved guidelines matching user query
        search_results = repository.search(user_message, security_classification=clearance)
        # Filters to only include APPROVED or ACTIVE guidance
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

    # 2. Assemble Context-Augmented Prompt
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

    # 3. Query OpenAI
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
        # Mock reply if API key is not configured for local integration testing
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
            # Format outputs as a list of match records
            return jsonify({"results": results}), 200
        else:
            cards = repository.list_cards()
            # Apply basic manual filters if present
            if card_type:
                cards = [c for c in cards if c.card_type.upper() == card_type.upper()]
            if tag:
                cards = [c for c in cards if tag.lower() in [ct.lower() for ct in c.tags]]
            if security:
                cards = [c for c in cards if c.security_classification == security]

            return jsonify({"cards": [c.to_dict() for c in cards]}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list cards: {e}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
