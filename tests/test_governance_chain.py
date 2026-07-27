import os
import sqlite3
from services.solomon_governance_approval_packet import GovernanceApprovalLane

def test_governance_hash_chain_creation(tmp_path):
    test_log = os.path.join(tmp_path, "test_governance.bin")
    test_db = os.path.join(tmp_path, "test_solomon.db")

    lane = GovernanceApprovalLane(log_file=test_log, db_path=test_db)

    # 1. Add some decisions
    lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    lane.review_packet({"requires_approval": True, "approved_by": "Mark"})

    # 2. Verify that the chain compiles and validates successfully
    assert lane.verify_governance_chain() is True

def test_governance_tamper_detection(tmp_path):
    test_log = os.path.join(tmp_path, "test_governance.bin")
    test_db = os.path.join(tmp_path, "test_solomon.db")

    lane = GovernanceApprovalLane(log_file=test_log, db_path=test_db)

    # Add multiple decisions to form a chain
    lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    lane.review_packet({"requires_approval": True, "approved_by": "Mark"})

    # Verify first
    assert lane.verify_governance_chain() is True

    # 3. Inject malicious tampering into a past record
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE governance_events SET decision = 'approved' WHERE sequence = 1")
    conn.commit()
    conn.close()

    # 4. Verify that tamper detection correctly flags the broken hash chain
    assert lane.verify_governance_chain() is False
