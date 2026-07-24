from typing import List, Dict, Any
import json

class DynamicContextEngine:
    def __init__(self, max_vram_mb: int = 1500):
        self.max_vram_mb = max_vram_mb
        self.bytes_per_mb = 1024 * 1024
        self.swap_file = "cold_context_swap.bin"

    def budget_context(self, current_vram_usage: float, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        available_vram = self.max_vram_mb - current_vram_usage

        # Phase 22: Context Importance Weighting Assignment
        for i, msg in enumerate(messages):
            if "importance" not in msg:
                msg["importance"] = 1.0 if msg.get("role") == "system" else 0.5

        messages = self._deduplicate_messages(messages)

        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_vram = (total_chars * 10) / self.bytes_per_mb

        if estimated_vram > available_vram:
            return self._compress_messages(messages, target_vram=available_vram)
        return messages

    def _deduplicate_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped = []
        last_hash = None
        for msg in messages:
            msg_hash = hash(msg.get("content", ""))
            if msg_hash != last_hash:
                deduped.append(msg)
                last_hash = msg_hash
        return deduped

    def _swap_to_disk(self, message: Dict[str, Any]):
        with open(self.swap_file, "a") as f:
            f.write(json.dumps(message) + "\n")

    def _compress_messages(self, messages: List[Dict[str, Any]], target_vram: float) -> List[Dict[str, Any]]:
        compressed = messages[:]
        while len(compressed) > 3:
            total_chars = sum(len(m.get("content", "")) for m in compressed)
            if (total_chars * 10) / self.bytes_per_mb <= target_vram:
                break

            # Phase 22: Delete lowest importance first, prioritizing user chat over system context
            idx_to_remove = -1
            min_importance = float('inf')

            for i in range(1, len(compressed)):
                imp = compressed[i].get("importance", 0.5)
                if imp < min_importance:
                    min_importance = imp
                    idx_to_remove = i

            if idx_to_remove != -1:
                self._swap_to_disk(compressed[idx_to_remove])
                compressed.pop(idx_to_remove)
            else:
                break

        if len(compressed) < len(messages):
            compressed.insert(0, {"role": "system", "content": "[PREVIOUS CONTEXT COMPRESSED BY IMPORTANCE SCORE]"})
        return compressed
