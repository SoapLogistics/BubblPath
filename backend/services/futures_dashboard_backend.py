import json
import os
from services.solomon_futures_engine import FuturesEngine
from services.solomon_governance_approval_packet import GovernanceApprovalLane

route_key = "solomon_futures_dashboard"

class FuturesDashboardBackend:
    def __init__(self):
        self.engine = FuturesEngine()
        self.governance = GovernanceApprovalLane()

    def get_projections(self):
        """
        Mock retrieval of actual futures projections to feed the dashboard.
        In a real scenario, this reads from the output of the daily scan.
        """
        # Read from daily scan context if available, otherwise mock
        projections = []

        try:
            # Simulate processing of mock targets for UI display
            targets = [
                {"id": "tgt_alpha", "conf": 92.5},
                {"id": "tgt_beta", "conf": 81.2},
                {"id": "tgt_gamma", "conf": 75.0}
            ]

            for t in targets:
                proj = self.engine.generate_projection(t["id"], t["conf"], {"raw": "data"})
                projections.append(proj)

            return {"status": "success", "projections": projections}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_action(self, packet):
        """
        Gated by the Governance Lane.
        """
        # Send through governance approval
        gov_result = self.governance.review_packet(packet)

        if gov_result.get("status") == "refused":
            return gov_result

        return {"status": "success", "audit_id": gov_result.get("audit_id", "aud_auto")}
