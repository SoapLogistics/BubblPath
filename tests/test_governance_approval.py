from services.solomon_governance_approval_packet import GovernanceApprovalLane

def test_refusal_without_mark():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    assert res["status"] == "refused"

def test_approval_with_mark():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Mark"})
    assert res["status"] == "approved"

def test_failed_validation_blocks_promotion():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"validation_status": "failed"})
    assert res["status"] == "refused"
    assert "Failed validation" in res["reason"]

def test_high_risk_actions_require_approval_and_ss3():
    lane = GovernanceApprovalLane()
    # No approval, no ss3
    res = lane.review_packet({"action": "jules_subprocess"})
    assert res["status"] == "refused"

    # Only mark approval
    res = lane.review_packet({"action": "git_push", "approved_by": "Mark"})
    assert res["status"] == "refused"

    # Both approval and ss3
    res = lane.review_packet({"action": "sudo", "approved_by": "Mark", "ss3_verified": True})
    assert res["status"] == "approved"

def test_ss1_requires_rollback_procedure():
    lane = GovernanceApprovalLane()
    # Missing rollback procedure
    res = lane.review_packet({"target_environment": "SS1", "approved_by": "Mark", "ss3_verified": True})
    assert res["status"] == "refused"
    assert "rollback_procedure" in res["reason"]

    # Has rollback procedure
    res = lane.review_packet({
        "target_environment": "SS1",
        "rollback_procedure": "Restore DB snapshot",
        "approved_by": "Mark"
    })
    assert res["status"] == "approved"

def test_rollback_restores_state():
    lane = GovernanceApprovalLane()
    res = lane.rollback("aud_003")
    assert res["status"] == "rolled_back"
    assert "database" in res["restored_components"]
    assert "memory_checkpoint" in res["restored_components"]
