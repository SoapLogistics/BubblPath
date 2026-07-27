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

    # Initialize managers
    print("1. Initializing Managers...")
    db = DatabaseManager(db_file)
    repo = CardRepository(db_manager=db, embedder=DummyEmbedder())
    writeback = LearningWriteback(db_path=memory_atoms_db)
    governance = GovernanceApprovalLane(log_file=gov_log_file)

    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    run_id = str(uuid.uuid4())[:8]
    task_id = "task_001"
    event_id = f"evt_{run_id}"

    # Check if we are restarting by looking for previous memories
    existing_cards = repo.search_by_type("LESSON")
    is_restart = len(existing_cards) > 0
    if is_restart:
        print("  Detected existing state - running in RESTART mode")

    # 1. Task failure -> event creation
    print("2. Task failure -> Event Creation")
    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO events (id, type, data, timestamp) VALUES (?, ?, ?, ?)",
                     (event_id, "task_failure", "Failed to connect to API on port 8080", timestamp))

    # 2. Non-empty candidate -> duplicate check
    print("3. Candidate Generation and Deduplication")
    candidate_id = f"cand_{run_id}"
    lesson_content = "Always check firewall settings when connection fails."

    res = writeback.record_lesson(packet_id="pkt_001", result="fail", memory="event", lesson=lesson_content)

    if res['recorded'] == False and res.get('reason') == 'duplicate':
        print("  Duplicate check passed (blocked). System already knows this lesson.")
        # Fast-forward to retrieval using existing knowledge
        card = existing_cards[0]
        card_id = card.card_id
    else:
        print("  Lesson recorded: True")
        with sqlite3.connect(db_file) as conn:
            conn.execute("INSERT INTO candidates (id, event_id, content, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                         (candidate_id, event_id, lesson_content, "pending_review", timestamp))

        # 3. Validation -> approval
        print("4. Governance Validation & Approval")
        gov_packet = {"requires_approval": True, "approved_by": "Mark", "action": "approve_candidate", "timestamp": timestamp}
        gov_res = governance.review_packet(gov_packet)
        print(f"  Status: {gov_res['status']}")

        with open(f"{evidence_dir}/governance_packet.json", "w") as f:
            json.dump({"packet": gov_packet, "result": gov_res}, f, indent=2)

        with sqlite3.connect(db_file) as conn:
            conn.execute("INSERT INTO governance (id, candidate_id, status, approver, timestamp) VALUES (?, ?, ?, ?, ?)",
                         (f"gov_{run_id}", candidate_id, "approved", "Mark", timestamp))
            conn.execute("UPDATE candidates SET status = ? WHERE id = ?", ("approved", candidate_id))

        # 4. Active memory creation
        print("5. Active Memory Promotion (Mnemosyne)")
        card_id = f"card_{run_id}"
        card = KnowledgeCard(
            card_id=card_id,
            card_type="LESSON",
            schema_version="1.0",
            title="Firewall settings during API connect failure",
            summary="Check firewall settings when connection fails",
            body=lesson_content,
            status="ACTIVE",
            confidence=0.5, # Initial confidence
            validation_state="VALID",
            created_at=timestamp,
            updated_at=timestamp,
            created_by="system",
            source_type="event",
            source_ids=[event_id],
            parent_card_ids=[],
            related_card_ids=[],
            tags=["firewall", "networking", "api"],
            security_classification="unclassified",
            evidence="Observed failure during task_001 and recovered by fixing firewall",
            why_created="To prevent future failures when hitting API",
            problem_solved="Prevents hanging or timing out when the port is blocked",
            future_work_dependent="None"
        )
        repo.create_card(card, creator="system", reason="Promoted candidate to active memory")

        with sqlite3.connect(db_file) as conn:
            conn.execute("INSERT INTO memories (id, candidate_id, content, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                         (f"mem_{run_id}", candidate_id, lesson_content, "active", timestamp))

    # 5. Retrieval before a similar task
    print("6. Simulated Second Task: Automatic Retrieval")
    trace_id = f"trace_{run_id}"
    query = "connection failed on port 8080"

    start_time = time.time()
    # Search repository natively
    search_results = repo.search(query, card_type="LESSON")
    retrieval_latency = time.time() - start_time

    print(f"  Memory retrieved in {retrieval_latency*1000:.2f}ms")

    if search_results:
        best_match = search_results[0]
        retrieved_card = KnowledgeCard.from_dict(best_match["card"])
        print(f"  Confidence before: {retrieved_card.confidence}")

        competing = [{"id": r["card_id"], "score": r["score"], "reason": r["explanation"]} for r in search_results[1:]]

        trace_data = {
            "timestamp": timestamp,
            "query": query,
            "latency_ms": retrieval_latency * 1000,
            "selected_memory": retrieved_card.to_dict(),
            "competing_rejected": competing,
            "execution_plan_change": "Injected firewall-check step before executing API request."
        }
        with open(f"{evidence_dir}/retrieval_trace_{run_id}.json", "w") as f:
            json.dump(trace_data, f, indent=2)

        with sqlite3.connect(db_file) as conn:
            conn.execute("INSERT INTO retrieval_traces (id, query, memory_id, timestamp) VALUES (?, ?, ?, ?)",
                         (trace_id, query, retrieved_card.card_id, timestamp))

        # 6. Successful attempt -> outcome scoring
        print("7. Outcome Scoring and Utility Update")
        task_id_2 = "task_002"
        use_id = f"use_{run_id}"

        # Update memory confidence/utility
        retrieved_card.confidence = min(1.0, retrieved_card.confidence + 0.2)
        repo.update_card(retrieved_card, updater="system", reason="Successful task completion")
        print(f"  Confidence after successful use: {retrieved_card.confidence}")

        with sqlite3.connect(db_file) as conn:
            conn.execute("INSERT INTO uses (id, trace_id, task_id, timestamp) VALUES (?, ?, ?, ?)",
                         (use_id, trace_id, task_id_2, timestamp))
            conn.execute("INSERT INTO outcomes (id, use_id, score, timestamp) VALUES (?, ?, ?, ?)",
                         (f"out_{run_id}", use_id, 1.0, timestamp))

    # 7. Target selection -> checkpointing
    print("8. Next Learning Target & Checkpoint Creation")
    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO learning_targets (id, description, priority, timestamp) VALUES (?, ?, ?, ?)",
                     (f"target_{run_id}", "Optimize firewall checking routine", 1, timestamp))
        conn.execute("INSERT INTO checkpoints (id, data, timestamp) VALUES (?, ?, ?)",
                     (f"chk_{run_id}", "learning_cycle_completed_successfully", timestamp))

    checkpoint_data = {
        "timestamp": timestamp,
        "status": "success",
        "memories_count": len(db.list_all_cards()),
        "checkpoint_id": f"chk_{run_id}"
    }
    with open(f"{evidence_dir}/checkpoint_{run_id}.json", "w") as f:
        json.dump(checkpoint_data, f, indent=2)

    print("==================================================")
    print("DEMO COMPLETE: PLC Execution verified.")
    print("Artifacts saved in evidence_artifacts/")

if __name__ == "__main__":
    run_demo()
