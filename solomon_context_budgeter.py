class DynamicContextBudgeter:
    """
    SOSS Phase 20: Dynamic Context Budgeter
    Evaluates system-wide available memory (RAM/VRAM) to scale character limits dynamically
    and prunes prompt histories to fit allocations safely using sliding context,
    adaptive retrieval, and semantic prioritization.
    """
    def __init__(self, db=None):
        self.db = db

    def evaluate_budget(self, available_ram_mb, available_vram_mb, history):
        # 1. Scale character limits dynamically based on memory
        total_mem = available_ram_mb + available_vram_mb
        dynamic_char_limit = int(total_mem * 5) # e.g., 5 chars per MB

        if dynamic_char_limit < 500:
            dynamic_char_limit = 500

        # 2. Semantic Prioritization and Sliding Context
        # We assume history items might be dictionaries with 'content' and 'semantic_score'
        # If they are just strings, we treat them as recent items.

        processed_history = []
        for idx, item in enumerate(history):
            if isinstance(item, dict):
                content = item.get('content', '')
                score = item.get('semantic_score', 1.0)
                # boost recent items slightly to combine sliding context + semantic prioritization
                recency_boost = (idx / len(history)) * 0.5 if len(history) > 0 else 0
                processed_history.append({
                    'original': item,
                    'content': content,
                    'score': score + recency_boost,
                    'idx': idx
                })
            else:
                # String item
                recency_boost = (idx / len(history)) * 0.5 if len(history) > 0 else 0
                processed_history.append({
                    'original': item,
                    'content': str(item),
                    'score': 1.0 + recency_boost,
                    'idx': idx
                })

        # Sort by score descending (Semantic Prioritization)
        processed_history.sort(key=lambda x: x['score'], reverse=True)

        # 3. Adaptive Retrieval: Prune to fit dynamic limit
        pruned_history = []
        current_len = 0

        for item in processed_history:
            item_len = len(item['content'])
            if current_len + item_len <= dynamic_char_limit:
                pruned_history.append(item)
                current_len += item_len

        # Restore original order for the sliding context output
        pruned_history.sort(key=lambda x: x['idx'])

        final_history = [item['original'] for item in pruned_history]

        return {
            "dynamic_char_limit": dynamic_char_limit,
            "pruned_history_count": len(final_history),
            "original_history_count": len(history),
            "pruned_history": final_history,
            "available_ram_mb": available_ram_mb,
            "available_vram_mb": available_vram_mb,
            "strategy": "sliding context with semantic prioritization"
        }
