import os
import pytest
from services.solomon_governance_approval_packet import GovernanceApprovalLane

def test_refusal_without_mark():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    assert res["status"] == "refused"

def test_approval_with_mark():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Mark"})
    assert res["status"] == "approved"

def test_ss1_promotion_blocked_missing_rollback():
    """
    MD6 Promotion Gate: Strictly block promotions to SS1 if rollback_procedure is missing.
    """
    lane = GovernanceApprovalLane()
    res = lane.review_packet({
        "packet_id": "pkg_001",
        "environment": "SS1",
        "action": "deploy_web_service",
        "author": "Mark",
        "validation_success": True
    })
    assert res["status"] == "refused"
    assert "missing 'rollback_procedure'" in res["reason"]

def test_ss1_promotion_blocked_failed_validation():
    """
    MD6 Promotion Gate: Strictly block promotions to SS1 if validation fails.
    """
    lane = GovernanceApprovalLane()
    res = lane.review_packet({
        "packet_id": "pkg_002",
        "environment": "SS1",
        "action": "deploy_web_service",
        "author": "Mark",
        "rollback_procedure": "git revert HEAD",
        "validation_failed": True
    })
    assert res["status"] == "refused"
    assert "validation failed" in res["reason"]

def test_ss1_promotion_approved_and_audited_256_bytes():
    """
    MD6 Promotion Gate: Verify successful SS1 promotion and its 256-byte O(1) audit log write/read.
    """
    # Delete file if exists to ensure starting indexing from 0 in our test
    log_file = "governance_log.bin"
    if os.path.exists(log_file):
        os.remove(log_file)

    lane = GovernanceApprovalLane()

    packet = {
        "packet_id": "pkg_12345",
        "environment": "SS1",
        "action": "mutate_database",
        "author": "Mark Miller",
        "validation_hash": "val_hash_7788",
        "rollback_hash": "roll_hash_9900",
        "rollback_procedure": "sqlite3 solomon_soss.db < backup.sql",
        "validation_success": True
    }

    res = lane.review_packet(packet)
    assert res["status"] == "approved"

    # Read the audit log from index 0
    audit = lane.read_audit_log(0)
    assert audit is not None
    assert audit["packet_id"] == "pkg_12345"
    assert audit["environment"] == "SS1"
    assert audit["status"] == "approved"
    assert audit["action"] == "mutate_database"
    assert audit["author"] == "Mark Miller"
    assert audit["validation_hash"] == "val_hash_7788"
    assert audit["rollback_hash"] == "roll_hash_9900"
    assert audit["timestamp"] > 0
