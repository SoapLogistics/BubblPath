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
from solomon_knowledge_cards.planner.engine import DynamicPlanner
from solomon_knowledge_cards.planner.arbiter import ToolArbiter

def print_separator(title: str):
    print("\n" + "="*80)
    print(f" {title.upper()} ".center(80, "="))
    print("="*80 + "\n")

def run_demo():
    print_separator("solomon cognitive os: project mnemosyne & prometheus e2e loop")

    # Initialize ephemeral SQLite database
    db_file = "solomon_cognitive_loop_demo.db"
    db_manager = DatabaseManager(db_file)
    repository = CardRepository(db_manager)
    graph_manager = RelationGraph(repository)
    proposal_eng = ProposalEngine(repository)
    reflection_eng = ReflectionSynthesizer(repository)
    extractor = KnowledgeExtractor()
    review_gate = ReviewGate(db_manager)
    planner = DynamicPlanner(repository)
    arbiter = ToolArbiter(repository)

    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # -------------------------------------------------------------
    # Step 1: Create baseline Procedure Card reference
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
        why_created="To establish operational playbook parameters.",
        problem_solved="Standardizes the deployment of OpenHands agent loops.",
        future_work_dependent="Forms the target for continuous capability improvements.",
        extra_metadata={"original_file_path": "openclaw-workspace/checklists/openhands_integration.md"}
    )
    repository.create_card(proc_card, creator="operator")
    print(f"Successfully registered Procedure Card: {proc_card.card_id} ('{proc_card.title}')")

    # -------------------------------------------------------------
    # Step 2: First Worker Run fails due to a Port busy conflict
    # -------------------------------------------------------------
    print("\n[2] Dispatching Task T-E2E-001 (First Run): Ingesting FAILURE Worker Report...")
    worker_report_1 = {
        "task_id": "T-E2E-001",
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

    draft_cards = extractor.extract_draft_cards(worker_report_1, creator="extractor")
    print(f"Extractor successfully generated {len(draft_cards)} draft candidates:")
    for card in draft_cards:
        print(f" - [{card.card_type}] {card.card_id}: '{card.title}'")
        repository.create_card(card, creator="extractor")

    # Promote Repair Card to ACTIVE
    print("\n[3] Promoting candidate cards through the explicit SS3 Review Gate...")
    repair_card = [c for c in draft_cards if c.card_type == "REPAIR"][0]
    review_gate.review_card(repair_card.card_id, notes="Verified port resolution playbook.")
    review_gate.approve_card(repair_card.card_id)
    review_gate.activate_card(repair_card.card_id)
    print(f"Repair Card {repair_card.card_id} is now ACTIVE.")

    # -------------------------------------------------------------
    # Step 4: Subsequent similar Task is dispatched -> Planner is queried
    # -------------------------------------------------------------
    print("\n[4] Dispatching Task T-E2E-002 (Second Run): Dynamic Planner formulates task plan...")
    plan_objective = "Deploy OpenHands Integration container on port 3000"
    print(f"Objective: '{plan_objective}'")

    # Dynamic planner drafts plan, querying memories
    plan = planner.draft_plan("T-E2E-002", plan_objective)
    print(f"Planner successfully retrieved {len(plan.retrieved_memory_card_ids)} memories from Mnemosyne: {plan.retrieved_memory_card_ids}")
    print(f"Injected Safeguards: {len(plan.injected_safeguards)}")
    for sg in plan.injected_safeguards:
        print(f"  * [Safeguard Injected] Triggered by {sg['triggered_by_repair']}: '{sg['remediation_instruction']}'")

    print("\nDrafted Steps Sequence:")
    for step in plan.steps:
        print(f"  {step['step_number']}. Action: '{step['action']}' (Tool: {step['tool']})")

    # -------------------------------------------------------------
    # Step 5: Execute Plan with Tool Configuration Arbitration
    # -------------------------------------------------------------
    print("\n[5] Simulating Plan Execution & executing Tool Arbitration on steps...")
    execution_history = []

    # Execute steps sequentially
    for step in plan.steps:
        action = step["action"]
        tool = step["tool"]

        # Tool config arbitration
        if tool in ("openhands_run", "bash_run"):
            base_config = {"port": 3000, "timeout_seconds": 30}
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

    print("\nExecution History Logs:")
    for h in execution_history:
        print(f"  * Step {h['step_number']} [{h['status']}]: '{h['action']}'")
        if "config_applied" in h:
            print(f"    Applied Tool Config: {h['config_applied']}")

    print("\nTask T-E2E-002 completed successfully! Self-healing loop completed.")

    # -------------------------------------------------------------
    # Step 6: Safe Procedure Proposal & Mutation Trigger
    # -------------------------------------------------------------
    print("\n[6] Proposing procedural update to canon operating checklist on disk...")
    proposal = proposal_eng.create_procedure_proposal(repair_card.card_id)
    print(f"Generated Proposal Card: {proposal.card_id} (Status: {proposal.status})")

    # Apply Proposal to checklists
    print("Promoting and applying proposal mutation...")
    review_gate.review_card(proposal.card_id, notes="Proposal verified.")
    review_gate.approve_card(proposal.card_id)
    success = proposal_eng.apply_proposal_to_disk(proposal.card_id)
    print(f"Procedural checklist mutated successfully: {success}")

    # -------------------------------------------------------------
    # Step 7: Topological Graph Query & Traversal
    # -------------------------------------------------------------
    print("\n[7] Querying semantic graph traversal and topological dependencies...")
    # Link Proposal to Procedure Card and PC-AC-01
    repository.link_cards(proposal.card_id, proc_card.card_id, "PROPOSES_UPDATE_TO")

    # Mock PC-AC-01 in the database so the link validation succeeds!
    pc_01 = KnowledgeCard(
        card_id="PC-AC-01", card_type="SKILL", schema_version="1.0.0", title="Master scheduler", summary="S", body="B",
        status="APPROVED", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=[],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repository.create_card(pc_01)
    repository.link_cards(proc_card.card_id, "PC-AC-01", "DEPENDS_ON")

    chain = graph_manager.find_dependency_chain("PC-AC-02")
    print(f"Topological execution dependencies for PC-AC-02: {chain}")

    # -------------------------------------------------------------
    # Step 8: Reinforcement Feedback
    # -------------------------------------------------------------
    print("\n[8] Simulating downstream success reinforcement feedback...")
    reinforced = reflection_eng.apply_reinforcement_feedback(repair_card.card_id, was_successful=True)
    print(f"Repair card {repair_card.card_id} confidence boosted: 0.70 -> {reinforced.confidence}")

    # Clean up demo database file
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"\nCleaned up database: {db_file}")

    temp_checklist = "openclaw-workspace/checklists/pc-doctrine-e2e.md"
    if os.path.exists(temp_checklist):
        os.remove(temp_checklist)

    print_separator("cognitive loop demo completed successfully")

if __name__ == "__main__":
    run_demo()
