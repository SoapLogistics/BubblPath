from services.solomon_governance_approval_packet import GovernanceGate

def test_governance_gate_refusal():
    gate = GovernanceGate()

    res = gate.request_execution("jules_subprocess", {}, {})
    assert res["status"] == "refusal"
    assert "Missing Mark approval" in res["reason"]

    res = gate.request_execution("ss1_mutation", {}, {"mark_approval": True})
    assert res["status"] == "refusal"
    assert "Missing SS3 review requirement" in res["reason"]

    res = gate.request_execution("git_push", {}, {"mark_approval": True, "ss3_review": True})
    assert res["status"] == "approved"
    assert "audit_id" in res
