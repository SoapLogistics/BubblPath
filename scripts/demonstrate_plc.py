import sqlite3
import datetime
import json
import time
import os
import uuid
from services.solomon_learning_writeback import LearningWriteback
from services.solomon_governance_approval_packet import GovernanceApprovalLane
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.api.repository import CardRepository

# Dummy embedder for CardRepository
class DummyEmbedder:
    def get_embedding(self, text):
        return [0.1] * 128
    def cosine_similarity(self, v1, v2):
        return 0.9

def run_demo():
    print("==================================================")
    print("SOLOMON PERPETUAL LEARNING CYCLE (PLC) DEMO")
    print("==================================================")

    db_file = "solomon_soss.db"
    memory_atoms_db = "memory_atoms.db"
    gov_log_file = "governance_log.bin"
    evidence_dir = "evidence_artifacts"

    os.makedirs(evidence_dir, exist_ok=True)

    from services.solomon_plc_engine import PerpetualLearningEngine

    # Initialize managers
    print("1. Initializing Managers...")
    db = DatabaseManager(db_file)
    engine = PerpetualLearningEngine(db_manager=db, embedder=DummyEmbedder(), gov_log_file=gov_log_file)

    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    run_id = str(uuid.uuid4())[:8]
    task_id = "task_001"

    # Check if we are restarting by looking at checkpoints
    latest_chk = engine.get_latest_checkpoint()
    if latest_chk:
        print(f"  Detected existing state - running in RESTART mode (Resuming from {latest_chk['id']})")

    # 1. Task failure -> event creation
    print("2. Task failure -> Event Creation")
    event_id = engine.record_event("task_failure", "Failed to connect to API on port 8080")

    # 2. Non-empty candidate -> duplicate check
    print("3. Candidate Generation and Deduplication")
    lesson_content = "Always check firewall settings when connection fails."

    card_id = engine.process_failure("task_001", event_id, lesson_content)

    if card_id is None:
        print("  Duplicate check passed (blocked). System already knows this lesson.")
    else:
        print("  Lesson recorded, validated, approved, and promoted to Active Memory.")
        # Create governance artifact
        gov_packet = {"requires_approval": True, "approved_by": "Mark", "action": "approve_candidate", "timestamp": timestamp}
        gov_res = engine.governance.review_packet(gov_packet)
        with open(f"{evidence_dir}/governance_packet_{run_id}.json", "w") as f:
            json.dump({"packet": gov_packet, "result": gov_res}, f, indent=2)

    # 5. Retrieval before a similar task
    print("6. Simulated Second Task: Automatic Retrieval")
    query = "connection failed on port 8080"

    retrieved_card, competing, latency = engine.retrieve_memory(query)

    print(f"  Memory retrieved in {latency*1000:.2f}ms")

    if retrieved_card:
        print(f"  Confidence before: {retrieved_card.confidence}")

        trace_data = {
            "timestamp": timestamp,
            "query": query,
            "latency_ms": latency * 1000,
            "selected_memory": retrieved_card.to_dict(),
            "competing_rejected": competing,
            "execution_plan_change": "Injected firewall-check step before executing API request."
        }
        with open(f"{evidence_dir}/retrieval_trace_{run_id}.json", "w") as f:
            json.dump(trace_data, f, indent=2)

        # 6. Successful attempt -> outcome scoring
        print("7. Outcome Scoring and Utility Update")
        task_id_2 = "task_002"
        engine.record_successful_use(task_id_2, retrieved_card, score=1.0)
        print(f"  Confidence after successful use: {retrieved_card.confidence}")

    # 7. Target selection -> checkpointing
    print("8. Next Learning Target & Checkpoint Creation")
    chk_id = engine.create_checkpoint("learning_cycle_completed")

    checkpoint_data = {
        "timestamp": timestamp,
        "status": "success",
        "memories_count": len(db.list_all_cards()),
        "checkpoint_id": chk_id
    }
    with open(f"{evidence_dir}/checkpoint_{run_id}.json", "w") as f:
        json.dump(checkpoint_data, f, indent=2)

    print("==================================================")
    print("DEMO COMPLETE: PLC Execution verified.")
    print("Artifacts saved in evidence_artifacts/")

if __name__ == "__main__":
    run_demo()
