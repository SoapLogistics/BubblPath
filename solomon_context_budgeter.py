"""
Solomon Perpetual Learning Machine
Phase 20: Dynamic Context Budgeter (solomon_context_budgeter.py)

This module implements the Dynamic Context Budgeter which monitors active
RAM/VRAM process constraints and dynamically scales down prompt sizes
or prunes message history to stay within budget limits.
"""

from typing import List, Dict, Any

class DynamicContextBudgeter:
    """
    Applies character and token-level context scaling based on current resource states.
    """

    @classmethod
    def budget_context(
        cls,
        history: List[Dict[str, str]],
        max_context_chars: int,
        system_ram_mb: float,
        critical_ram_threshold_mb: float = 1200.0
    ) -> Dict[str, Any]:
        """
        Calculates pruned history based on available RAM margins.
        """
        # If RAM is critical, dynamically drop context allowance by 50%
        effective_max_chars = max_context_chars
        warning_triggered = False

        if system_ram_mb >= critical_ram_threshold_mb:
            effective_max_chars = int(max_context_chars * 0.5)
            warning_triggered = True

        pruned_history = []
        current_char_count = 0

        # Traverse backwards to preserve most recent messages
        for msg in reversed(history):
            content_len = len(msg.get("content", ""))
            if current_char_count + content_len <= effective_max_chars:
                pruned_history.insert(0, msg)
                current_char_count += content_len
            else:
                break

        return {
            "original_messages_count": len(history),
            "pruned_messages_count": len(pruned_history),
            "effective_max_chars": effective_max_chars,
            "allocated_chars": current_char_count,
            "ram_warning_triggered": warning_triggered,
            "pruned_history": pruned_history
        }
