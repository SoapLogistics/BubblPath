from typing import List, Dict, Any
import math

class ContextBudgetPlanner:
    def __init__(
        self,
        model_context_window: int = 4096,
        system_prompt_reserve: int = 500,
        expected_response_reserve: int = 1000,
        safety_margin: int = 200
    ):
        self.model_context_window = model_context_window
        self.system_prompt_reserve = system_prompt_reserve
        self.expected_response_reserve = expected_response_reserve
        self.safety_margin = safety_margin

    def calculate_budget(self, task_input_size: int) -> int:
        available = (self.model_context_window
                     - self.system_prompt_reserve
                     - self.expected_response_reserve
                     - task_input_size
                     - self.safety_margin)
        return max(0, available)

    def retrieve_context(self, db, task_input: str, task_input_size: int, relevance_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Retrieves context in layered priority, stopping when budget is hit or relevance drops.
        """
        budget = self.calculate_budget(task_input_size)

        # Priority 1: Mandatory governance (we can mock this via family or focus)
        # Priority 2: Direct matches
        # Priority 3: Failures and repairs
        # Priority 4: Dependencies (if using graph)
        # Priority 5: Recent activity
        # Priority 6: Optional

        retrieved = []
        current_cost = 0

        # In a real system, you'd calculate exact tokens. Here we approximate 1 char = 0.25 tokens
        def estimate_tokens(text: str) -> int:
            return max(1, len(text) // 4)

        # Simplified query for now, fetching by semantic search and filtering by logic rules
        all_results = db.semantic_search(task_input, top_k=20)

        # Sort results into buckets
        governance = []
        direct_matches = []
        failures = []
        optional = []

        for r in all_results:
            family = r.get("family", "").lower()
            focus = r.get("focus", "").lower()

            if "safety" in family or "governance" in family:
                governance.append(r)
            elif "failure" in family or "repair" in family:
                failures.append(r)
            elif float(r.get("similarity", 0)) >= relevance_threshold:
                direct_matches.append(r)
            elif float(r.get("similarity", 0)) >= relevance_threshold - 0.2:
                optional.append(r)

        # Fill layers
        layers = [governance, direct_matches, failures, optional]

        for layer in layers:
            for item in layer:
                if any(r['card_id'] == item['card_id'] for r in retrieved):
                    continue
                cost = estimate_tokens(item["content"])
                if current_cost + cost <= budget:
                    retrieved.append(item)
                    current_cost += cost
                else:
                    pass # Skip if it doesn't fit, try smaller cards

        return retrieved
