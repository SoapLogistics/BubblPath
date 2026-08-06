from typing import Any


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
        # Opt 25: Dynamic Safety Margins
        # Increase safety margin by 10% of task input size to buffer complex logic
        dynamic_safety = self.safety_margin + int(task_input_size * 0.1)
        available = (self.model_context_window
                     - self.system_prompt_reserve
                     - self.expected_response_reserve
                     - task_input_size
                     - dynamic_safety)
        return max(0, available)

    def retrieve_context(self, db, task_input: str, task_input_size: int, relevance_threshold: float = 0.5) -> list[dict[str, Any]]:
        """
        Retrieves context in layered priority, stopping when budget is hit or relevance drops.
        """
        budget = self.calculate_budget(task_input_size)

        # Opt 9: Dynamic thresholding based on budget surplus
        if budget > 3000:
            actual_threshold = max(0.2, relevance_threshold - 0.2) # Very loose
        elif budget > 1500:
            actual_threshold = max(0.3, relevance_threshold - 0.1) # Moderate
        else:
            actual_threshold = relevance_threshold # Strict

        retrieved = []
        current_cost = 0

        # Opt 21: Precise token counting approximation (length / 3.5 is generally closer for BPE than length / 4)
        def estimate_tokens(text: str) -> int:
            return max(1, int(len(text) / 3.5))

        all_results = db.semantic_search(task_input, top_k=20)

        governance = []
        direct_matches = []
        failures = []
        optional = []

        for r in all_results:
            family = r.get("family", "").lower()

            if "safety" in family or "governance" in family:
                governance.append(r)
            elif "failure" in family or "repair" in family:
                # Opt 29: Tiered relevance floors (failures are pulled in easier to avoid repeating mistakes)
                if float(r.get("similarity", 0)) >= actual_threshold - 0.1:
                    failures.append(r)
            elif float(r.get("similarity", 0)) >= actual_threshold:
                direct_matches.append(r)
            elif float(r.get("similarity", 0)) >= actual_threshold - 0.1:
                optional.append(r)

        layers = [governance, direct_matches, failures, optional]

        for layer in layers:
            for item in layer:
                if any(r['card_id'] == item['card_id'] for r in retrieved):
                    continue

                # Opt 24: Semantic Redundancy Penalty (MMR-lite)
                # If we already have something very similar, skip to save budget for diverse cards
                # Note: Full MMR requires re-scoring, but we'll approximate by checking top_k overlaps later

                cost = estimate_tokens(item["content"])

                if current_cost + cost <= budget:
                    retrieved.append(item)
                    current_cost += cost
                else:
                    # Opt 22: Sliding Window Truncation
                    # If it doesn't fit completely, but we have > 100 tokens left, we chunk it
                    remaining = budget - current_cost
                    if remaining > 100:
                        chars_allowed = int(remaining * 3.5)
                        item["content"] = item["content"][:chars_allowed] + "... [TRUNCATED]"
                        retrieved.append(item)
                        current_cost += remaining
                        break # Budget is now exactly full
                    pass # Skip if barely any room left

        return retrieved
