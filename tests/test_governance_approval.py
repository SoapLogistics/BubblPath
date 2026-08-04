from services.solomon_governance_approval_packet import GovernanceApprovalLane


def test_refusal_without_mark():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    assert res["status"] == "refused"

def test_approval_with_mark():
    lane = GovernanceApprovalLane()
    res = lane.review_packet({"requires_approval": True, "approved_by": "Mark"})
    assert res["status"] == "approved"
