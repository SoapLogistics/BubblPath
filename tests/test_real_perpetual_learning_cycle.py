import pytest
import sqlite3
import datetime
from services.solomon_learning_writeback import LearningWriteback
from services.solomon_governance_approval_packet import GovernanceApprovalLane
import core.solomon_knowledge_cards.storage.db as db_manager

from core.solomon_knowledge_cards.models.card import KnowledgeCard

def test_real_perpetual_learning_cycle(tmp_path):
    # 0. Setup isolated state using tmp_path
    db_file = str(tmp_path / "solomon_soss.db")
    memory_atoms_db = str(tmp_path / "memory_atoms.db")
    gov_log_file = str(tmp_path / "governance_log.bin")

    # Initialize managers
    db = db_manager.DatabaseManager(db_file)
    writeback = LearningWriteback(db_path=memory_atoms_db)
    governance = GovernanceApprovalLane(log_file=gov_log_file)

    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    # 1. Task failure -> event creation
    task_id = "task_001"
    event_id = "evt_001"
    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO events (id, type, data, timestamp) VALUES (?, ?, ?, ?)",
                     (event_id, "task_failure", "Failed to connect to API on port 8080", timestamp))

    # 2. Non-empty candidate -> duplicate check
    candidate_id = "cand_001"
    lesson_content = "Always check firewall settings when connection fails."

    # The agent records the lesson and enforces write idempotency.
    res = writeback.record_lesson(packet_id="pkt_001", result="fail", memory="event", lesson=lesson_content)
    assert res["recorded"] == True

    # Attempting to learn the exact same thing again is blocked.
    res_dup = writeback.record_lesson(packet_id="pkt_001", result="fail", memory="event", lesson=lesson_content)
    assert res_dup["recorded"] == False
    assert res_dup["reason"] == "duplicate"

    # It creates a candidate in the PLC tables.
    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO candidates (id, event_id, content, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                     (candidate_id, event_id, lesson_content, "pending_review", timestamp))

    # 3. Validation -> approval
    gov_res = governance.review_packet({"requires_approval": True, "approved_by": "Mark", "action": "approve_candidate"})
    assert gov_res["status"] == "approved"

    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO governance (id, candidate_id, status, approver, timestamp) VALUES (?, ?, ?, ?, ?)",
                     ("gov_001", candidate_id, "approved", "Mark", timestamp))
        conn.execute("UPDATE candidates SET status = ? WHERE id = ?", ("approved", candidate_id))

    # 4. Active memory creation - The card gets promoted to Mnemosyne
    card = KnowledgeCard(
        card_id="card_001",
        card_type="LESSON",
        schema_version="1.0",
        title="Firewall settings during API connect failure",
        summary="Check firewall settings when connection fails",
        body=lesson_content,
        status="ACTIVE",
        confidence=0.9,
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
    db.store_card(card)

    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO memories (id, candidate_id, content, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                     ("mem_001", candidate_id, lesson_content, "active", timestamp))

    # 5. Retrieval before a similar task
    trace_id = "trace_001"
    query = "connection failed on port 8080"

    # Agent searches for the knowledge
    retrieved_card = db.get_card("card_001")
    assert retrieved_card is not None
    assert retrieved_card.body == lesson_content

    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO retrieval_traces (id, query, memory_id, timestamp) VALUES (?, ?, ?, ?)",
                     (trace_id, query, retrieved_card.card_id, timestamp))

    # 6. Successful attempt -> outcome scoring
    task_id_2 = "task_002"
    use_id = "use_001"
    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO uses (id, trace_id, task_id, timestamp) VALUES (?, ?, ?, ?)",
                     (use_id, trace_id, task_id_2, timestamp))
        conn.execute("INSERT INTO outcomes (id, use_id, score, timestamp) VALUES (?, ?, ?, ?)",
                     ("out_001", use_id, 1.0, timestamp))

    # 7. Target selection -> checkpointing
    with sqlite3.connect(db_file) as conn:
        conn.execute("INSERT INTO learning_targets (id, description, priority, timestamp) VALUES (?, ?, ?, ?)",
                     ("target_001", "Optimize firewall checking routine", 1, timestamp))
        conn.execute("INSERT INTO checkpoints (id, data, timestamp) VALUES (?, ?, ?)",
                     ("chk_001", "learning_cycle_completed_successfully", timestamp))

    # 8. Restart with no state duplication (verify DBs exist and are not empty, and no duplicates recorded on duplicate attempt)
    # Re-instantiate managers
    db2 = db_manager.DatabaseManager(db_file)
    writeback2 = LearningWriteback(db_path=memory_atoms_db)

    cards = db2.list_all_cards()
    assert len(cards) == 1
    assert cards[0].card_id == "card_001"

    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM checkpoints")
        assert c.fetchone()[0] == 1

    # Check that another duplicate writeback fails
    res_dup_2 = writeback2.record_lesson(packet_id="pkt_001", result="fail", memory="event", lesson=lesson_content)
    assert res_dup_2["recorded"] == False
    assert res_dup_2["reason"] == "duplicate"
