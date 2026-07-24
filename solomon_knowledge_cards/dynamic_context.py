from typing import List, Dict, Any
import os
import json

class DynamicContextEngine:
    def __init__(self, max_vram_mb: int = 1500):
        self.max_vram_mb = max_vram_mb
        self.bytes_per_mb = 1024 * 1024
        self.swap_file = "cold_context_swap.bin" # Phase 12

    def budget_context(self, current_vram_usage: float, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        available_vram = self.max_vram_mb - current_vram_usage

        messages = self._deduplicate_messages(messages)

        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_vram = (total_chars * 10) / self.bytes_per_mb

        if estimated_vram > available_vram:
            return self._compress_messages(messages, target_vram=available_vram)
        return messages

    def _deduplicate_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        deduped = []
        last_hash = None
        for msg in messages:
            msg_hash = hash(msg.get("content", ""))
            if msg_hash != last_hash:
                deduped.append(msg)
                last_hash = msg_hash
        return deduped

    # Phase 12: Cold Memory Disk Swapping
    def _swap_to_disk(self, message: Dict[str, str]):
        with open(self.swap_file, "a") as f:
            f.write(json.dumps(message) + "\n")

    def _compress_messages(self, messages: List[Dict[str, str]], target_vram: float) -> List[Dict[str, str]]:
        compressed = messages[:]
        while len(compressed) > 3:
            total_chars = sum(len(m.get("content", "")) for m in compressed)
            if (total_chars * 10) / self.bytes_per_mb <= target_vram:
                break

            idx_to_remove = -1
            for i in range(1, len(compressed)):
                if compressed[i].get("role") != "system":
                    idx_to_remove = i
                    break

            if idx_to_remove != -1:
                # Phase 12: Swap to disk instead of just deleting
                self._swap_to_disk(compressed[idx_to_remove])
                compressed.pop(idx_to_remove)
            else:
                break

        if len(compressed) < len(messages):
            compressed.insert(0, {"role": "system", "content": "[PREVIOUS CONTEXT SUMMARIZED AND SWAPPED TO DISK]"})
        return compressed
