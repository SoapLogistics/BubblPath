from services.solomon_governance_approval_packet import GovernanceApprovalLane
import os
import struct
import mmap

def test_refusal_without_mark():
    if os.path.exists("governance_log.bin"):
        os.remove("governance_log.bin")
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    assert res["status"] == "refused"

def test_approval_with_mark():
    if os.path.exists("governance_log.bin"):
        os.remove("governance_log.bin")
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Mark"})
    assert res["status"] == "approved"

def test_high_risk_refusal_without_context():
    if os.path.exists("governance_log.bin"):
        os.remove("governance_log.bin")
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"action": "jules_subprocess"})
    assert res["status"] == "refused"
    assert "High-risk actions" in res["reason"]

def test_high_risk_approval_with_context():
    if os.path.exists("governance_log.bin"):
        os.remove("governance_log.bin")
    lane = GovernanceApprovalLane()
    res = lane.review_packet({
        "action": "jules_subprocess",
        "mark_approval": True,
        "ss3_review": True
    })
    assert res["status"] == "approved"

def test_audit_history_and_o1_append():
    if os.path.exists("governance_log.bin"):
        os.remove("governance_log.bin")

    lane = GovernanceApprovalLane()

    # Generate an audit trail
    lane.review_packet({"action": "unknown", "requires_approval": True, "approved_by": "Nobody"})
    lane.review_packet({"action": "test_action_approved", "requires_approval": True, "approved_by": "Mark"})

    history = lane.get_audit_history(limit=2)

    assert len(history) == 2
    assert history[0]["status"] == "approved"
    assert history[0]["action"] == "test_action_approved"

    assert history[1]["status"] == "refused"
    assert history[1]["action"] == "unknown"
