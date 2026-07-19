import datetime
import uuid
import json
from solomon_knowledge_cards.models.card import KnowledgeCard
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.extractor.extractor import KnowledgeExtractor
from solomon_knowledge_cards.api.review import ReviewGate

def print_separator(title: str):
    print("\n" + "="*80)
    print(f" {title.upper()} ".center(80, "="))
    print("="*80 + "\n")

def run_demo():
    print_separator("project mnemosyne: end-to-end learning loop demo")

    # Initialize ephemeral SQLite database
    db_file = "solomon_mnemosyne_demo.db"
    db_manager = DatabaseManager(db_file)
    repository = CardRepository(db_manager)
    extractor = KnowledgeExtractor()
    review_gate = ReviewGate(db_manager)

    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # -------------------------------------------------------------
    # Step 1: Create a Procedure Card Reference
    # -------------------------------------------------------------
    print("[1] Creating baseline Procedure Card reference...")
    proc_card = KnowledgeCard(
        card_id="PC-AC-02",
        card_type="SKILL",
        schema_version="1.0.0",
        title="Deploy OpenHands Integration Service",
        summary="Standard playbook for orchestrating and launching OpenHands agent container.",
        body="Steps:\n1. Check port availability.\n2. Spin up OpenHands docker container.\n3. Verify HTTP API health.",
        status="APPROVED",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="operator",
        source_type="LEGACY_DOCTRINE",
        source_ids=["openclaw-workspace/checklists/openhands_integration.md"],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["deployment", "docker", "openhands"],
        security_classification="INTERNAL",
        evidence="Active production service configuration file.",
        why_created="To establish operational playbook parameters for OpenHands execution.",
        problem_solved="Standardizes the deployment of OpenHands agent loops.",
        future_work_dependent="Forms the target for continuous capability improvements."
    )
    repository.create_card(proc_card, creator="operator")
    print(f"Successfully registered Procedure Card: {proc_card.card_id} ('{proc_card.title}')")

    # -------------------------------------------------------------
    # Step 2: Create a Task Card Reference
    # -------------------------------------------------------------
    print("\n[2] Creating ephemeral Task Card dispatch reference...")
    task_id = "TASK-E2E-101"
    # We will record the task execution details in a Worker Report.

    # -------------------------------------------------------------
    # Step 3: Worker Execution & Ingestion
    # -------------------------------------------------------------
    print("\n[3] Simulating Worker execution and receiving Worker Report...")
    # This report contains details about a container start failure (port conflict)
    # and a successful recovery check.
    worker_report = {
        "task_id": task_id,
        "procedure_id": "PC-AC-02",
        "title": "OpenHands environment execution",
        "outcome": "failure",
        "attempted": "Launched openhands on default port 3000 to process user tasks.",
        "succeeded": "Initialized memory context files, parsed instruction logs.",
        "failed": "Docker launch failed because port 3000 was already bound by background process.",
        "root_cause": "A rogue node server was listening on port 3000, preventing Docker socket binding.",
        "repair_action": "Set environment variables to port 3001, or run: kill $(lsof -t -i :3000) before launch.",
        "evidence": "Docker error log: 'bind: address already in use 0.0.0.0:3000'",
        "tags": ["timeout", "docker", "port-conflict"]
    }
    print(f"Ingested Worker Report for Task: {task_id}")
    print(f"Outcome: {worker_report['outcome'].upper()}")
    print(f"Failed Components: {worker_report['failed']}")

    # -------------------------------------------------------------
    # Step 4: Submit SS3 Review Result
    # -------------------------------------------------------------
    print("\n[4] Submitting SS3 Review and Evaluation Result...")
    review_result = {
        "review_id": "REV-E2E-202",
        "is_valid": True,
        "confidence_score": 0.95,
        "notes": "Agree. Rogue process blocking port 3000 is a common local dev environment issue. The repair action is fully correct."
    }
    print(f"SS3 Review Submitted: VALID = {review_result['is_valid']}, Confidence = {review_result['confidence_score']}")

    # -------------------------------------------------------------
    # Step 5: Ingestion into Knowledge Cards (Extraction Engine)
    # -------------------------------------------------------------
    print("\n[5] Feeding Worker Report & Review Result to the extraction engine...")
    draft_cards = extractor.extract_draft_cards(worker_report, review_result, creator="extractor")
    print(f"Extractor generated {len(draft_cards)} candidate cards:")
    for card in draft_cards:
        print(f" - [{card.card_type}] {card.card_id}: '{card.title}' (Status: {card.status})")
        # Save draft card to DB
        repository.create_card(card, creator="extractor", reason="Extracted from Task Run")

    # -------------------------------------------------------------
    # Step 6: Review Gate Promotion Process
    # -------------------------------------------------------------
    print("\n[6] Promoting candidate cards through the explicit Review Gate...")
    approved_cards = []
    for card in draft_cards:
        print(f"Processing candidate: {card.card_id} ({card.card_type})")
        # Promote from DRAFT -> REVIEWED
        print(f"  -> Reviewing card {card.card_id}...")
        reviewed = review_gate.review_card(card.card_id, notes="Approved during automatic e2e validation cycle.", updater="reviewer")
        print(f"  -> Status: {reviewed.status}")

        # Promote from REVIEWED -> APPROVED
        print(f"  -> Approving card {card.card_id}...")
        approved = review_gate.approve_card(card.card_id, updater="approver")
        print(f"  -> Status: {approved.status} (Validation State: {approved.validation_state})")

        # Promote from APPROVED -> ACTIVE
        print(f"  -> Activating card {card.card_id}...")
        active = review_gate.activate_card(card.card_id, updater="operator")
        print(f"  -> Status: {active.status}")
        approved_cards.append(active)

    # -------------------------------------------------------------
    # Step 7: Retrieval and Search Query
    # -------------------------------------------------------------
    print("\n[7] Querying memory store for prior failures or repairs...")
    search_query = "port conflict on openhands"
    print(f"Executing Query: '{search_query}'")
    search_results = repository.search(search_query)

    print(f"Search retrieved {len(search_results)} matched memories:")
    for idx, res in enumerate(search_results, start=1):
        print(f"Match {idx}:")
        print(f"  * Card ID: {res['card_id']}")
        print(f"  * Type: {res['card_type']}")
        print(f"  * Score: {res['score']:.2f}")
        print(f"  * Explanation: {res['explanation']}")
        print(f"  * Summary: {res['card']['summary']}")
        print(f"  * Problem Solved: {res['card']['problem_solved']}")
        print(f"  * Why Created: {res['card']['why_created']}")

    # -------------------------------------------------------------
    # Step 8: Retrieve Approved Repair Playbook & Related References
    # -------------------------------------------------------------
    print("\n[8] Retrieving specific remediation playbook and related links...")
    # Find the repair card from approved cards
    repair_card_id = [c.card_id for c in approved_cards if c.card_type == "REPAIR"][0]
    repair_details = repository.get_card(repair_card_id)
    print(f"Remediation Playbook Card: {repair_details.card_id}")
    print(f"Body:\n---\n{repair_details.body}\n---")

    # Fetch related failure card reference
    print(f"Linked failures:")
    for rel_id in repair_details.related_card_ids:
        rel_card = repository.get_card(rel_id)
        if rel_card:
            print(f"  - [{rel_card.card_type}] {rel_card.card_id}: '{rel_card.title}'")

    # -------------------------------------------------------------
    # Step 9: Revision and Provenance Chain
    # -------------------------------------------------------------
    print("\n[9] Displaying complete audit trail and provenance chain...")
    revisions = repository.retrieve_revision_history(repair_card_id)
    print(f"Audit Log for {repair_card_id}:")
    for rev in revisions:
        print(f"  * Revision {rev['revision_number']} (Timestamp: {rev['updated_at']})")
        print(f"    Author: {rev['updated_by']}")
        print(f"    Action / Reason: {rev['reason']}")
        print(f"    Staged Title: '{rev['serialized_card']['title']}'")
        print(f"    Status state: {rev['serialized_card']['status']}")

    # Clean up demo database file
    import os
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"\nCleaned up database: {db_file}")

    print_separator("demo successfully completed")

if __name__ == "__main__":
    run_demo()
