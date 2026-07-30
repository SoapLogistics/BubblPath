import time
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

def test_revocation():
    lane = GovernanceApprovalLane()
    lane.revoke_approval("deploy_feature_abc")
    res = lane.review_packet({"action": "deploy_feature_abc", "requires_approval": True, "approved_by": "Mark"})
    assert res["status"] == "refused"
    assert "revoked" in res["reason"]

def test_expiration():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({
        "action": "some_expired_action",
        "requires_approval": True,
        "approved_by": "Mark",
        "timestamp": time.time() - 7200,  # 2 hours ago
        "expires_at": time.time() - 3600  # expired 1 hour ago
    })
    assert res["status"] == "refused"
    assert "expired" in res["reason"]

def test_audit_integrity_verification():
    lane = GovernanceApprovalLane()
    # Trigger several approvals to generate chain records
    lane.review_packet({"action": "action1", "requires_approval": True, "approved_by": "Mark"})
    lane.review_packet({"action": "action2", "requires_approval": True, "approved_by": "Mark"})
    lane.review_packet({"action": "action3", "requires_approval": True, "approved_by": "Mark"})

    # Verify cryptographic integrity
    assert lane.verify_integrity() is True

def test_self_approval():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({
        "action": "self_approve_action",
        "requires_approval": True,
        "requester": "Mark",
        "approved_by": "Mark"
    })
    assert res["status"] == "refused"
    assert "self-approval is forbidden" in res["reason"]
