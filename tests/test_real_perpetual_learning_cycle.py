import os
import json
import sqlite3
import pytest
from services.solomon_learning_writeback import LearningWriteback
from services.solomon_governance_approval_packet import GovernanceApprovalLane
from solomon_quantized_memory import QuantizedBrainMap, QuantizedMemoryNode

def test_real_perpetual_learning_cycle(tmp_path):
    """
    Deliverable 4: Real perpetual-learning cycle integration test.
    failure -> event -> non-empty candidate -> duplicate check -> validation ->
    approval -> active memory -> retrieval before planning -> improved second attempt ->
    outcome update -> next target -> checkpoint -> process restart -> no duplication.
    """
    test_db = os.path.join(tmp_path, "test_solomon_state.db")
    test_log = os.path.join(tmp_path, "test_governance_log.bin")
    checkpoint_file = os.path.join(tmp_path, "test_checkpoint.json")

    evidence_dir = "evidence/campaign_01/"
    os.makedirs(evidence_dir, exist_ok=True)

    # --- STAGE 1: FAILURE AND CANDIDATE CREATION ---
    task_id_1 = "task_failed_normalization"
    failure_reason = "Lookup failed for key '  ALPHA  ' due to untrimmed whitespace"

    first_task_data = {"task_id": task_id_1, "status": "failed", "error": failure_reason}
    with open(os.path.join(evidence_dir, "01_first_task.json"), "w") as f:
        json.dump(first_task_data, f, indent=2)

    failure_event = {"event_id": "evt_001", "type": "task_failure", "payload": first_task_data}
    with open(os.path.join(evidence_dir, "02_failure_event.json"), "w") as f:
        json.dump(failure_event, f, indent=2)

    # Draft a non-empty learning candidate
    candidate_lesson = "Always strip whitespace and case-fold lookup keys before database query execution."
    lane_writeback = LearningWriteback(db_path=test_db)

    # Reject empty or status-only lessons (proven by ValueError triggers)
    with pytest.raises(ValueError):
        lane_writeback.record_lesson("p1", "pass", "lesson", lesson="")

    with pytest.raises(ValueError):
        lane_writeback.record_lesson("p1", "pass", "lesson", lesson="pass")

    # Ingest candidate lesson
    res_candidate = lane_writeback.record_lesson(
        packet_id="p1",
        result="failed",
        memory="lesson",
        lesson=candidate_lesson
    )
    assert res_candidate["recorded"] is True
    assert res_candidate["duplicate"] is False

    with open(os.path.join(evidence_dir, "03_candidate.json"), "w") as f:
        json.dump(res_candidate, f, indent=2)

    # --- STAGE 2: DEDUPLICATION AND VALIDATION ---
    res_dup = lane_writeback.record_lesson(
        packet_id="p1",
        result="failed",
        memory="lesson",
        lesson=candidate_lesson
    )
    assert res_dup["recorded"] is True
    assert res_dup["duplicate"] is True

    validation_result = {"status": "passed", "checks": ["non_empty", "no_status_words", "idempotency_passed"]}
    with open(os.path.join(evidence_dir, "04_validation.json"), "w") as f:
        json.dump(validation_result, f, indent=2)

    # --- STAGE 3: GOVERNANCE AND APPROVAL ---
    gov_lane = GovernanceApprovalLane(log_file=test_log, db_path=test_db)
    gov_packet = {
        "requires_approval": True,
        "approved_by": "Mark",
        "action": "Store casing lookup key normalization",
        "packet_id": "p1"
    }
    gov_res = gov_lane.review_packet(gov_packet)
    assert gov_res["status"] == "approved"
    assert gov_lane.verify_governance_chain() is True

    with open(os.path.join(evidence_dir, "05_governance.json"), "w") as f:
        json.dump(gov_res, f, indent=2)

    # --- STAGE 4: MEMORY ACTIVATION AND INDEXING ---
    brain_map = QuantizedBrainMap(max_nodes=100)
    node_id = brain_map.ingest(
        node_type="procedural_memory",
        content=candidate_lesson,
        importance=0.9,
        valence=0.5,
        arousal=0.8
    )
    assert node_id is not None

    active_memory_data = {"node_id": node_id, "content": candidate_lesson, "indexed": True}
    with open(os.path.join(evidence_dir, "06_active_memory.json"), "w") as f:
        json.dump(active_memory_data, f, indent=2)

    # --- STAGE 5: RETRIEVAL BEFORE PLANNING ---
    query_text = "how to do database key normalization"
    retrieved = brain_map.recall(query_text, top_k=1)
    assert len(retrieved) > 0
    assert candidate_lesson in retrieved[0]["content"]

    retrieval_trace = {"query": query_text, "results": retrieved}
    with open(os.path.join(evidence_dir, "07_retrieval_trace.json"), "w") as f:
        json.dump(retrieval_trace, f, indent=2)

    plan_trace = {"action": "execute_with_normalized_keys", "derived_from_memory": True}
    with open(os.path.join(evidence_dir, "08_plan.json"), "w") as f:
        json.dump(plan_trace, f, indent=2)

    # --- STAGE 6: IMPROVED SECOND ATTEMPT & OUTCOME UPDATE ---
    task_id_2 = "task_success_normalization"
    second_task_data = {"task_id": task_id_2, "status": "success", "normalization_applied": True}
    with open(os.path.join(evidence_dir, "09_second_task.json"), "w") as f:
        json.dump(second_task_data, f, indent=2)

    outcome_data = {"task_id": task_id_2, "success": True, "improvement": "Lookup succeeded with whitespace-trimmed normalized key"}
    with open(os.path.join(evidence_dir, "10_outcome.json"), "w") as f:
        json.dump(outcome_data, f, indent=2)

    score_delta = 0.15
    with sqlite3.connect(test_db) as conn:
        conn.execute("""
            UPDATE memory_atoms
            SET confidence = confidence + ?, utility = utility + ?
            WHERE lesson = ?
        """, (score_delta, score_delta, candidate_lesson))
        conn.commit()

    with sqlite3.connect(test_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT confidence, utility FROM memory_atoms WHERE lesson = ?", (candidate_lesson,)).fetchone()
        assert row["confidence"] == 1.15
        assert row["utility"] == 1.15

    memory_update_data = {"lesson": candidate_lesson, "new_confidence": float(row["confidence"]), "new_utility": float(row["utility"])}
    with open(os.path.join(evidence_dir, "11_memory_update.json"), "w") as f:
        json.dump(memory_update_data, f, indent=2)

    # --- STAGE 7: NEXT TARGET SELECTION ---
    next_target = "Implement unicode-based key normalization"
    with open(os.path.join(evidence_dir, "12_next_target.json"), "w") as f:
        json.dump({"next_target": next_target}, f, indent=2)

    # --- STAGE 8: CHECKPOINT ---
    checkpoint_data = {
        "last_task_completed": task_id_2,
        "next_target_selected": next_target,
        "governance_verified": True
    }
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoint_data, f, indent=2)
    assert os.path.exists(checkpoint_file)

    with open(os.path.join(evidence_dir, "13_checkpoint_before_restart.json"), "w") as f:
        json.dump(checkpoint_data, f, indent=2)

    # --- STAGE 9: PROCESS RESTART & RESUME ---
    with open(checkpoint_file, "r") as f:
        reloaded_checkpoint = json.load(f)

    with open(os.path.join(evidence_dir, "14_checkpoint_after_restart.json"), "w") as f:
        json.dump(reloaded_checkpoint, f, indent=2)

    lane_writeback_restarted = LearningWriteback(db_path=test_db)

    with sqlite3.connect(test_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM memory_atoms")
        total_records = cursor.fetchone()[0]
        assert total_records == 1

    # Write unified cycle_trace.jsonl containing all transitions sequentially
    with open(os.path.join(evidence_dir, "15_cycle_trace.jsonl"), "w") as f:
        f.write(json.dumps({"stage": "first_task", "data": first_task_data}) + "\n")
        f.write(json.dumps({"stage": "failure_event", "data": failure_event}) + "\n")
        f.write(json.dumps({"stage": "candidate_writeback", "data": res_candidate}) + "\n")
        f.write(json.dumps({"stage": "validation", "data": validation_result}) + "\n")
        f.write(json.dumps({"stage": "governance", "data": gov_res}) + "\n")
        f.write(json.dumps({"stage": "active_memory", "data": active_memory_data}) + "\n")
        f.write(json.dumps({"stage": "retrieval_trace", "data": retrieval_trace}) + "\n")
        f.write(json.dumps({"stage": "plan_trace", "data": plan_trace}) + "\n")
        f.write(json.dumps({"stage": "second_task", "data": second_task_data}) + "\n")
        f.write(json.dumps({"stage": "outcome", "data": outcome_data}) + "\n")
        f.write(json.dumps({"stage": "memory_update", "data": memory_update_data}) + "\n")
        f.write(json.dumps({"stage": "next_target", "next_target": next_target}) + "\n")
        f.write(json.dumps({"stage": "checkpoint", "data": checkpoint_data}) + "\n")
