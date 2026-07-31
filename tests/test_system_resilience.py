import pytest
import os
import sqlite3
import hashlib
from services.solomon_governance_approval_packet import GovernanceApprovalLane

def test_tampered_backup_detected(tmp_path):
    """
    Simulates checking a database backup for tampering.
    In actual implementation, there would be a manifest or checksum.
    Here, we simulate standard resilience tests.
    """
    db_path = tmp_path / "backup.db"

    # Create fake db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE records (id INTEGER, data TEXT)")
    cursor.execute("INSERT INTO records VALUES (1, 'original')")
    conn.commit()
    conn.close()

    # Hash it
    with open(db_path, "rb") as f:
        original_hash = hashlib.sha256(f.read()).hexdigest()

    # Tamper it
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET data = 'tampered' WHERE id = 1")
    conn.commit()
    conn.close()

    # Check
    with open(db_path, "rb") as f:
        new_hash = hashlib.sha256(f.read()).hexdigest()

    assert original_hash != new_hash, "Tampered backup should have a different hash!"

def test_unauthorized_promotion_blocked():
    """
    Tests that unauthorized promotions (missing SS3 verification or wrong approver) are blocked.
    """
    lane = GovernanceApprovalLane()

    # Missing correct approver
    packet = {
        "action": "promote_to_ss1",
        "requires_approval": True,
        "approved_by": "Jules"
    }
    result = lane.review_packet(packet)
    assert result["status"] == "refused"
    assert result["reason"] == "Requires Mark approval"

    # Missing SS3 verification
    packet = {
        "action": "promote_to_ss1",
        "requires_approval": False,
        "requires_ss3_review": True,
        "ss3_verified": False
    }
    result = lane.review_packet(packet)
    assert result["status"] == "refused"
    assert result["reason"] == "Requires SS3 verification"

    # Authorized
    packet = {
        "action": "promote_to_ss1",
        "requires_approval": True,
        "approved_by": "Mark",
        "requires_ss3_review": True,
        "ss3_verified": True
    }
    result = lane.review_packet(packet)
    assert result["status"] == "approved"
