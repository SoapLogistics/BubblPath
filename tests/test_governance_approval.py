import os
from services.solomon_governance_approval_packet import GovernanceApprovalLane

def test_refusal_without_mark(tmp_path):
    log_file = str(tmp_path / "governance_log.bin")
    lane = GovernanceApprovalLane(log_file=log_file)
    res = lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    assert res["status"] == "refused"

def test_approval_with_mark(tmp_path):
    log_file = str(tmp_path / "governance_log.bin")
    lane = GovernanceApprovalLane(log_file=log_file)
    res = lane.review_packet({"requires_approval": True, "approved_by": "Mark"})
    assert res["status"] == "approved"
