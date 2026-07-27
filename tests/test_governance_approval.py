import os
from services.solomon_governance_approval_packet import GovernanceApprovalLane

def test_refusal_without_mark(tmp_path):
    test_log = os.path.join(tmp_path, "test_governance_log.bin")
    lane = GovernanceApprovalLane(log_file=test_log)
    res = lane.review_packet({"requires_approval": True, "approved_by": "Nobody"})
    assert res["status"] == "refused"

def test_approval_with_mark(tmp_path):
    test_log = os.path.join(tmp_path, "test_governance_log.bin")
    lane = GovernanceApprovalLane(log_file=test_log)
    res = lane.review_packet({"requires_approval": True, "approved_by": "Mark"})
    assert res["status"] == "approved"
