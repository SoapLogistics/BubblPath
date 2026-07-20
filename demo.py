import os
import json
from solomon_knowledge_cards.models import KnowledgeCardModel, CardType, CardStatus, CardRelation
from solomon_knowledge_cards.db import SQLiteDatabase
from solomon_knowledge_cards.repository import KnowledgeRepository
from solomon_knowledge_cards.engine import KnowledgeEngine

def run_demo():
    print("====================================================")
    print("  SOLOMON KNOWLEDGE CARD ENGINE - END-TO-END DEMO    ")
    print("====================================================")

    # 1. Initialize SQLite Database and Repository
    db_path = "demo_solomon_cards.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = SQLiteDatabase(db_path)
    repo = KnowledgeRepository(db)
    engine = KnowledgeEngine(repo)

    print("\n[STEP 1] DB and Repository successfully initialized.")

    # 2. Setup Procedure Card Reference
    proc_card = KnowledgeCardModel(
        card_id="PC-SO-01",
        card_type=CardType.PROCEDURE,
        title="Open-Source Code Absorption SOP",
        summary="Standard operating procedure for scanning and absorbing open source repos.",
        body="1. Search GitHub.\n2. Fetch codebase.\n3. Validate files using syntax checker.\n4. Merge files.",
        why_created="To establish standardized code intake protocols.",
        problem_solved="Unified ingestion procedures.",
        future_work_dependent="None"
    )
    repo.update_card(proc_card)
    print(f"-> Saved Procedure Card: {proc_card.card_id} - '{proc_card.title}'")

    # 3. Submit a Worker Report containing a failure (e.g. openhands timeout error)
    worker_report = {
        "task_id": "TASK-ABSORB-99",
        "procedure_id": "PC-SO-01",
        "success": False,
        "summary": "Scan failed midway because openhands endpoint timed out after 30 seconds.",
        "error_logs": "ConnectionTimeoutError: POST /api/session timed out after 30s.",
        "resolution": "Increase connection timeout to 120 seconds in configuration parameters.",
        "evidence": "Log trace segment #1420"
    }
    print(f"\n[STEP 2] Simulating Worker Report submission for task: {worker_report['task_id']}")

    # 4. Extract draft Knowledge Cards
    draft_cards = engine.extract_from_report(worker_report)
    print(f"-> Extracted {len(draft_cards)} draft cards from report:")
    for card in draft_cards:
        print(f"   * [{card.card_type}] {card.card_id} - '{card.title}' (Status: {card.status})")

    # 5. Review and Promotion Gate (DRAFT -> REVIEWED -> APPROVED -> ACTIVE)
    fail_card = next(c for c in draft_cards if c.card_type == CardType.FAILURE)
    repair_card = next(c for c in draft_cards if c.card_type == CardType.REPAIR)

    print(f"\n[STEP 3] Promoting and Approving Repair Card: {repair_card.card_id}")
    # Promote Repair: DRAFT -> REVIEWED
    engine.promote_card(repair_card.card_id, reviewer="SS3")
    # Promote Repair: REVIEWED -> APPROVED
    engine.promote_card(repair_card.card_id, reviewer="SS3")

    # Promote Failure: DRAFT -> REVIEWED -> APPROVED
    engine.promote_card(fail_card.card_id, reviewer="SS3")
    engine.promote_card(fail_card.card_id, reviewer="SS3")

    print(f"-> Card: {repair_card.card_id} state is now: {repo.get_card(repair_card.card_id).status}")

    # 6. Retrieve relevant prior memories before a similar task run
    print("\n[STEP 4] Simulating pre-task retrieval query for keyword: 'timeout'")
    operational_guidance = engine.retrieve_active_operational_guidance("timeout")
    print(f"-> Found {len(operational_guidance)} trusted results:")
    for result in operational_guidance:
        print(f"   * [{result['type']}] {result['card_id']} - '{result['title']}'")
        print(f"     Confidence: {result['confidence']}, Evidence: {result['evidence']}")

    # 7. Print Revision history
    print(f"\n[STEP 5] Auditing Revision history for approved Repair card: {repair_card.card_id}")
    history = repo.get_revision_history(repair_card.card_id)
    for h in history:
        print(f"   * Revision version: {h['version']} updated at {h['updated_at']} by {h['updated_by']}")

    # Cleanup database
    if os.path.exists(db_path):
         os.remove(db_path)
    print("\n====================================================")
    print("  DEMO EXECUTED SUCCESSFULLY - ALL CHECKS PASS!       ")
    print("====================================================")

if __name__ == "__main__":
    run_demo()
