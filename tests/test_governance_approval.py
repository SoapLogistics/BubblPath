import os
import pytest
from services.solomon_governance_approval_packet import GovernanceApprovalLane

@pytest.fixture
def lane():
    log_file = "test_governance_log.bin"
    if os.path.exists(log_file):
        os.remove(log_file)
    lane = GovernanceApprovalLane(log_file=log_file)
    yield lane
    if os.path.exists(log_file):
        os.remove(log_file)

def test_refusal_without_mark(lane):
    res = lane.review_packet({"requires_approval": True, "approved_by": "Nobody", "packet_id": "p1"})
    assert res["status"] == "refused"

def test_approval_with_mark(lane):
    res = lane.review_packet({"requires_approval": True, "approved_by": "Mark", "packet_id": "p2"})
    assert res["status"] == "approved"

def test_high_risk_action_requires_mark_and_ss3(lane):
    # Missing both
    res = lane.review_packet({"action": "ss1_mutation", "packet_id": "p3"})
    assert res["status"] == "refused"
    assert "Mark" in res["reason"]

    # Missing SS3
    res = lane.review_packet({"action": "ss1_mutation", "approved_by": "Mark", "packet_id": "p4"})
    assert res["status"] == "refused"
    assert "SS3" in res["reason"]

    # Has both
    res = lane.review_packet({"action": "ss1_mutation", "approved_by": "Mark", "ss3_verified": True, "packet_id": "p5"})
    assert res["status"] == "approved"

def test_promotion_flow_ss2_to_ss1_blocked(lane):
    packet = {
        "packet_id": "p6",
        "environment": "SS2",
        "target_environment": "SS1"
    }
    res = lane.promote_packet(packet)
    assert res["status"] == "refused"
    assert "SS3" in res["reason"]

def test_promotion_flow_ss3_to_ss1_allowed(lane):
    packet = {
        "packet_id": "p7",
        "environment": "SS3",
        "target_environment": "SS1"
    }
    res = lane.promote_packet(packet)
    assert res["status"] == "promoted"

def test_rollback(lane):
    rollback_hash = "hash_12345"
    packet = {
        "packet_id": "p8",
        "action": "deploy",
        "rollback_hash": rollback_hash
    }
    # Log an event
    lane._audit_event(packet, "approved")

    # Perform rollback
    res = lane.rollback(rollback_hash)
    assert res["status"] == "rolled_back"
    assert res["rollback_hash"] == rollback_hash

    # Rollback non-existent hash
    res2 = lane.rollback("does_not_exist")
    assert res2["status"] == "failed"
