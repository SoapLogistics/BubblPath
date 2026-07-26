import json
import uuid

class GovernanceGate:
    def __init__(self):
        self.blocked_capabilities = [
            "jules_subprocess",
            "worker_activation",
            "ss1_mutation",
            "git_push",
            "ssh",
            "sudo",
            "production_deployment",
            "browser_action_execution",
            "network_mutation_beyond_approved_data_fetch",
            "model_weight_promotion",
            "scheduler_promotion"
        ]

    def request_execution(self, capability: str, payload: dict, approval_context: dict):
        if capability in self.blocked_capabilities:
            if approval_context.get("mark_approval") is not True:
                return {
                    "status": "refusal",
                    "reason": "Missing Mark approval",
                    "audit_id": str(uuid.uuid4())
                }
            if approval_context.get("ss3_review") is not True:
                return {
                    "status": "refusal",
                    "reason": "Missing SS3 review requirement",
                    "audit_id": str(uuid.uuid4())
                }

        return {
            "status": "approved",
            "audit_id": str(uuid.uuid4())
        }
