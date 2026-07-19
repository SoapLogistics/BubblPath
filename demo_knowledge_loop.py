import datetime
import uuid
import json
import os
from solomon_knowledge_cards.models.card import KnowledgeCard
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.api.graph import RelationGraph
from solomon_knowledge_cards.extractor.extractor import KnowledgeExtractor
from solomon_knowledge_cards.extractor.proposal_engine import ProposalEngine
from solomon_knowledge_cards.extractor.reflection import ReflectionSynthesizer
from solomon_knowledge_cards.api.review import ReviewGate

def print_separator(title: str):
    print("\n" + "="*80)
    print(f" {title.upper()} ".center(80, "="))
    print("="*80 + "\n")

def run_demo():
    print_separator("project mnemosyne: phase 3b advanced cognitive learning loop")

    # Initialize ephemeral SQLite database
    db_file = "solomon_mnemosyne_phase3b_demo.db"
    db_manager = DatabaseManager(db_file)
    repository = CardRepository(db_manager)
    graph_manager = RelationGraph(repository)
    proposal_eng = ProposalEngine(repository)
    reflection_eng = ReflectionSynthesizer(repository)
    extractor = KnowledgeExtractor()
    review_gate = ReviewGate(db_manager)

    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # -------------------------------------------------------------
    # Step 1: Create baseline Procedure Card references
    # -------------------------------------------------------------
    print("[1] Creating baseline Procedure Card references...")
    proc_card_1 = KnowledgeCard(
        card_id="PC-AC-01",
        card_type="SKILL",
        schema_version="1.0.0",
        title="24/7 Continuous Autonomous Cycle",
        summary="Master scheduler loops.",
        body="Periodic scheduling loop checklist.",
        status="APPROVED",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="operator",
        source_type="LEGACY_DOCTRINE",
        source_ids=["openclaw-workspace/checklists/autonomous_cycle.md"],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["scheduling", "heartbeat"],
        security_classification="INTERNAL",
        evidence="Active production service configuration file.",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future",
        extra_metadata={"original_file_path": "openclaw-workspace/checklists/autonomous_cycle.md"}
    )
    repository.create_card(proc_card_1, creator="operator")

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
        why_created="To establish operational playbook parameters.",
        problem_solved="Standardizes the deployment of OpenHands agent loops.",
        future_work_dependent="Forms the target for continuous capability improvements.",
        extra_metadata={"original_file_path": "openclaw-workspace/checklists/openhands_integration.md"}
    )
    repository.create_card(proc_card, creator="operator")
    print(f"Successfully registered Procedure Cards: PC-AC-01 and PC-AC-02.")

    # -------------------------------------------------------------
    # Step 2: Ingest failure Worker Report (Docker Port Conflict)
    # -------------------------------------------------------------
    print("\n[2] Ingesting failure Worker Report...")
    worker_report = {
        "task_id": "TASK-E2E-301",
        "procedure_id": "PC-AC-02",
        "title": "OpenHands environment execution",
        "outcome": "failure",
        "attempted": "Launched openhands on default port 3000 to process user tasks.",
        "succeeded": "Initialized memory context files, parsed instruction logs.",
        "failed": "Docker launch failed because port 3000 was already bound by background process.",
        "root_cause": "A rogue node server was listening on port 3000, preventing Docker socket binding.",
        "repair_action": "Set environment variables to port 3001, or run: kill $(lsof -t -i :3000) before launch.",
        "evidence": "Docker error log: 'bind: address already in use 0.0.0.0:3000'",
        "tags": ["docker", "port-conflict"]
    }

    # Extract draft cards
    draft_cards = extractor.extract_draft_cards(worker_report, creator="extractor")
    print(f"Extractor generated {len(draft_cards)} draft candidates:")
    for card in draft_cards:
        print(f" - [{card.card_type}] {card.card_id}: '{card.title}'")
        repository.create_card(card, creator="extractor")

    # Promote cards to ACTIVE
    print("\n[3] Reviewing and Approving the extracted Repair Card...")
    repair_card = [c for c in draft_cards if c.card_type == "REPAIR"][0]
    review_gate.review_card(repair_card.card_id, notes="Verified port resolution playbook.")
    review_gate.approve_card(repair_card.card_id)
    review_gate.activate_card(repair_card.card_id)

    # -------------------------------------------------------------
    # Step 4: Propose Procedural Update (Safe Mutation)
    # -------------------------------------------------------------
    print("\n[4] Generating a Safe Procedural Amendment Proposal...")
    proposal = proposal_eng.create_procedure_proposal(repair_card.card_id)
    print(f"Generated proposal card: {proposal.card_id} (Status: {proposal.status})")
    print(f"Proposal Details:\n---\n{proposal.body}\n---")

    # Try dry-run mutation (must fail because proposal is in DRAFT status)
    print("Attempting to apply proposal to checklists file on disk...")
    success_before = proposal_eng.apply_proposal_to_disk(proposal.card_id)
    print(f"Dry-run mutation applied: {success_before} (Expected: False due to DRAFT status)")

    # Promote Proposal Card to APPROVED
    review_gate.review_card(proposal.card_id, notes="Proposed modification is safe.")
    review_gate.approve_card(proposal.card_id)

    # Apply Proposal to Disk (must succeed now!)
    print("Applying approved proposal to checklists file on disk...")
    success_after = proposal_eng.apply_proposal_to_disk(proposal.card_id)
    print(f"Mutation applied: {success_after} (Expected: True due to APPROVED status)")

    # -------------------------------------------------------------
    # Step 5: Semantic Relation Graph Queries
    # -------------------------------------------------------------
    print("\n[5] Establishing Semantic Graph relations and querying Graph Traversal...")
    # Link Proposal to the Repair Card and Procedure Card
    repository.link_cards(proposal.card_id, proc_card.card_id, "PROPOSES_UPDATE_TO")
    repository.link_cards(proc_card.card_id, "PC-AC-01", "DEPENDS_ON")

    # Query dependency chain for PC-AC-02
    chain = graph_manager.find_dependency_chain("PC-AC-02")
    print(f"Topological dependency chain for PC-AC-02: {chain}")

    # Retrieve local subgraph
    subgraph = graph_manager.get_subgraph(proposal.card_id, max_depth=2)
    print(f"Retrieved surrounding semantic subgraph nodes for {proposal.card_id}:")
    for n in subgraph["nodes"]:
        print(f"  * Node {n['card_id']} ({n['card_type']}): '{n['title']}' (Status: {n['status']})")
    print(f"Subgraph Edges:")
    for e in subgraph["edges"]:
        print(f"  * {e['source']} -- [{e['type']}] --> {e['target']}")

    # -------------------------------------------------------------
    # Step 6: Hybrid Semantic Search Ranking
    # -------------------------------------------------------------
    print("\n[6] Performing Hybrid Lexical-Semantic query search...")
    query = "timeout on openhands container startup"
    print(f"Query: '{query}'")
    results = repository.search(query)
    for idx, r in enumerate(results[:3], start=1):
        print(f"Match {idx} [Score: {r['score']:.2f}]:")
        print(f"  * Card: {r['card_id']} ({r['card_type']})")
        print(f"  * Explanation: {r['explanation']}")

    # -------------------------------------------------------------
    # Step 7: Reflection & Synthesis (Creating RESEARCH objectives)
    # -------------------------------------------------------------
    print("\n[7] Simulating autonomous reflection to synthesize RESEARCH objectives...")
    # Add a second timeout failure to trigger reflection
    fail_card_2 = KnowledgeCard(
        card_id="FC-TIMEOUT-ALT", card_type="FAILURE", schema_version="1.0.0", title="Docker compile timeout", summary="S", body="Encountered docker compile timeout.",
        status="DRAFT", confidence=0.8, validation_state="UNVALIDATED", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=["timeout"],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repository.create_card(fail_card_2)

    # Trigger reflection analysis
    researches = reflection_eng.analyze_failures_and_synthesize_research()
    print(f"Reflection analyzed failures and synthesized {len(researches)} new RESEARCH cards:")
    for res in researches:
        print(f"  * RESEARCH Card: {res.card_id} ('{res.title}')")
        print(f"    Summary: {res.summary}")

    # -------------------------------------------------------------
    # Step 8: Reinforcement Confidence Auto-Adjustment
    # -------------------------------------------------------------
    print("\n[8] Simulating reinforcement feedback loops on REPAIR cards...")
    target_repair_id = repair_card.card_id
    current_card = repository.get_card(target_repair_id)
    print(f"Target card: {current_card.card_id} (Confidence: {current_card.confidence}, Status: {current_card.status})")

    # Simulate a successful execution referencing this repair card
    print("Downstream worker successfully applies repair. Sending positive reinforcement...")
    reinforced = reflection_eng.apply_reinforcement_feedback(target_repair_id, was_successful=True)
    print(f"  -> Reinforced Confidence: {reinforced.confidence}")

    # Simulate recurring failures indicating the repair is no longer effective
    print("Downstream worker hits failures despite applying repair. Sending negative reinforcement decays...")
    decayed = reflection_eng.apply_reinforcement_feedback(target_repair_id, was_successful=False)
    print(f"  -> Decay 1: {decayed.confidence}")
    decayed = reflection_eng.apply_reinforcement_feedback(target_repair_id, was_successful=False)
    print(f"  -> Decay 2: {decayed.confidence}")
    decayed = reflection_eng.apply_reinforcement_feedback(target_repair_id, was_successful=False)
    print(f"  -> Decay 3: {decayed.confidence}")
    decayed = reflection_eng.apply_reinforcement_feedback(target_repair_id, was_successful=False)
    print(f"  -> Decay 4: {decayed.confidence}")
    decayed = reflection_eng.apply_reinforcement_feedback(target_repair_id, was_successful=False)
    print(f"  -> Decay 5: {decayed.confidence}")

    print(f"Final state for {target_repair_id}: Status = {decayed.status}, Validation State = {decayed.validation_state} (Confidence: {decayed.confidence})")

    # Clean up demo database file and temp procedure md
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"\nCleaned up database: {db_file}")

    temp_checklist = "openclaw-workspace/checklists/pc-doctrine-e2e.md"
    if os.path.exists(temp_checklist):
        os.remove(temp_checklist)

    print_separator("demo successfully completed")

if __name__ == "__main__":
    run_demo()
