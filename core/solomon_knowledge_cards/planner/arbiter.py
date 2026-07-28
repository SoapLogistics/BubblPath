from typing import Dict, Any, Optional
from core.solomon_knowledge_cards.api.repository import CardRepository

class ToolArbiter:
    def __init__(self, repository: CardRepository):
        self.repository = repository

    def arbitrate_tool_config(self, tool_name: str, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates memory cards matching the tool_name and dynamically adjusts base_config parameters
        (e.g., rewriting port numbers, increasing timeout thresholds) based on approved playbooks.
        """
        optimized_config = dict(base_config)

        # Retrieve active playbooks or repairs matching the tool_name
        search_results = self.repository.search(tool_name)
        active_repairs = [
            r["card"] for r in search_results
            if r["card_type"] == "REPAIR" and r["card"]["status"] in ("APPROVED", "ACTIVE")
        ]

        # Scan repairs for specific parameter adjust instructions
        for repair in active_repairs:
            body_lower = repair["body"].lower()

            # Port conflict adjustment rule
            if "port" in body_lower and "3000" in body_lower and "3001" in body_lower:
                if "port" in optimized_config and optimized_config["port"] == 3000:
                    optimized_config["port"] = 3001
                    optimized_config["arbitration_reason"] = f"Rewrote port 3000->3001 pre-emptively based on approved repair {repair['card_id']}."

            # Timeout extension rule
            if "timeout" in body_lower and "120" in body_lower:
                if "timeout_seconds" in optimized_config:
                    optimized_config["timeout_seconds"] = 120
                    optimized_config["arbitration_reason"] = f"Extended timeout threshold to 120s based on approved repair {repair['card_id']}."

        return optimized_config
