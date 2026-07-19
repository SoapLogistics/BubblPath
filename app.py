import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI

from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.extractor.extractor import KnowledgeExtractor
from solomon_knowledge_cards.api.review import ReviewGate
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


@app.route("/chat", methods=["POST"])
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
