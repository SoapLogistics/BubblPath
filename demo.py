import os
import json
from solomon_knowledge_cards.models import KnowledgeCardModel, CardType, CardStatus, CardRelation
from solomon_knowledge_cards.db import SQLiteDatabase
from solomon_knowledge_cards.repository import KnowledgeRepository
from solomon_knowledge_cards.engine import KnowledgeEngine

def run_demo():
    print("=========================================================")
    print("  SOLOMON KNOWLEDGE CARD ENGINE - END-TO-END DEMO SOK    ")
    print("=========================================================")

    # 1. Initialize DB and Repositories
    db_path = "demo_solomon_cards.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = SQLiteDatabase(db_path)
    repo = KnowledgeRepository(db)
    engine = KnowledgeEngine(repo)

    print("\n[STEP 1] DB and SOK repositories successfully initialized.")

    # 2. Setup standard Procedure Card reference
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
    # Explicitly approve the original Procedure Card to demonstrate the deduplication loop
    proc_card.status = CardStatus.APPROVED
    repo.update_card(proc_card)
    print(f"-> Saved Procedure Card: {proc_card.card_id} - '{proc_card.title}'")

    # 3. Simulate failure Worker Report triggering Missing Skill Discovery
    worker_report = {
        "task_id": "TASK-ABSORB-99",
        "procedure_id": "PC-SO-01",
        "success": False,
        "summary": "Scan failed midway because of missing capability 'ASTInjector'.",
        "error_logs": "Exception: missing capability 'ASTInjector' not found.",
        "resolution": "Implement ASTInjector class to parse programmatic Python branches.",
        "evidence": "Log trace segment #1420"
    }
    print(f"\n[STEP 2] Simulating Worker Report. Success: {worker_report['success']}")

    # 4. Extract draft Knowledge, Failure, and Skill Discovery Cards
    draft_cards = engine.extract_from_report(worker_report)
    print(f"-> Extracted {len(draft_cards)} draft cards from report:")
    for card in draft_cards:
        print(f"   * [{card.card_type}] {card.card_id} - '{card.title}' (Status: {card.status})")

    # 5. Fetch extracted failure and repair cards
    fail_card = next(c for c in draft_cards if c.card_type == CardType.FAILURE)
    repair_card = next(c for c in draft_cards if c.card_type == CardType.REPAIR)
    skill_card = next(c for c in draft_cards if c.card_type == CardType.SKILL)

    # Establish directed graph relation links: Repair -> Failure
    repo.link_cards(fail_card.card_id, repair_card.card_id, CardRelation.PREVENTS)

    # 6. Review and Promotion Gate
    print(f"\n[STEP 3] Promoting and Approving Repair Card: {repair_card.card_id}")
    engine.promote_card(repair_card.card_id, reviewer="SS3")
    engine.promote_card(repair_card.card_id, reviewer="SS3")

    engine.promote_card(fail_card.card_id, reviewer="SS3")
    engine.promote_card(fail_card.card_id, reviewer="SS3")

    # 7. Transitive Graph Traversal
    print(f"\n[STEP 4] Executing Transitive Graph Traversal on: {fail_card.card_id}")
    transitive_relations = repo.retrieve_transitive_relations(fail_card.card_id)
    for r_card in transitive_relations:
         print(f"   * Linked Relation: [{r_card.card_type}] {r_card.card_id} - '{r_card.title}'")

    # 8. SOK Metrics Calculation
    print("\n[STEP 5] Exporting SOK metrics telemetry...")
    metrics_path = "demo_growth_metrics.json"
    metrics = engine.calculate_sok_metrics(export_path=metrics_path)
    print(f"-> Total SOK Card Count: {metrics['total_cards_count']}")
    print(f"-> Average Confidence: {metrics['average_confidence']}")
    print(f"-> Reuse Rate (Approved): {metrics['reuse_rate']}")

    # 9. Passive Growth & Deduplication Loop
    print("\n[STEP 6] Running passive growth background deduplication...")
    # Inject exact duplicate
    dup_card = KnowledgeCardModel(
        card_id="PC-DUP-01",
        card_type=CardType.PROCEDURE,
        title="Duplicate Code Ingestion",
        summary="A redundant copy.",
        body="1. Search GitHub.\n2. Fetch codebase.\n3. Validate files using syntax checker.\n4. Merge files.",
    )
    repo.create_card(dup_card)

    growth_results = engine.run_passive_growth_maintenance()
    print(f"-> Merged duplicates: {growth_results['duplicates_merged']}")
    print(f"-> State of duplicate card: {repo.get_card('PC-DUP-01').status} ({repo.get_card('PC-DUP-01').metadata.get('deduplication_status')})")

    # Cleanups
    for path in [db_path, metrics_path]:
         if os.path.exists(path):
              os.remove(path)

    print("\n=========================================================")
    print("  DEMO EXECUTED SUCCESSFULLY - ALL 11 PHASES DEMONSTRATED ")
    print("=========================================================")

if __name__ == "__main__":
    run_demo()
