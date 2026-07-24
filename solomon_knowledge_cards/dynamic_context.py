from typing import List, Dict, Any
import json
import re
import hashlib

class DynamicContextEngine:
    def __init__(self, max_vram_mb: int = 1500):
        self.max_vram_mb = max_vram_mb
        self.bytes_per_mb = 1024 * 1024
        self.swap_file = "cold_context_swap.bin"
        self.semantic_cache = {} # Phase 66: Semantic Caching

    def budget_context(self, current_vram_usage: float, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        available_vram = self.max_vram_mb - current_vram_usage

        # Phase 68: Delta-Encoding Context (Stub: only pass recent diffs if large context)
        if len(messages) > 10:
            messages = [{"role": "system", "content": "[DELTA ENCODING ACTIVE]"}] + messages[-5:]

        for i, msg in enumerate(messages):
            if "importance" not in msg:
                msg["importance"] = 1.0 if msg.get("role") == "system" else 0.5

        messages = self._defragment_system_messages(messages)
        messages = self._deduplicate_messages(messages)

        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_vram = (total_chars * 10) / self.bytes_per_mb

        if estimated_vram > available_vram:
            messages = self._token_level_pruning(messages)
            total_chars = sum(len(m.get("content", "")) for m in messages)
            estimated_vram = (total_chars * 10) / self.bytes_per_mb
            if estimated_vram > available_vram:
                return self._compress_messages(messages, target_vram=available_vram)
        return messages

    # Phase 66
    def check_semantic_cache(self, messages: List[Dict[str, str]]) -> str:
        if not messages: return None
        # Hash the last user prompt
        last_prompt = messages[-1].get("content", "")
        prompt_hash = hashlib.sha256(last_prompt.encode()).hexdigest()
        return self.semantic_cache.get(prompt_hash)

    def add_to_cache(self, messages: List[Dict[str, str]], response: str):
        if not messages: return
        last_prompt = messages[-1].get("content", "")
        prompt_hash = hashlib.sha256(last_prompt.encode()).hexdigest()
        self.semantic_cache[prompt_hash] = response

    def _defragment_system_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        defragged, sys_content = [], []
        for msg in messages:
            if msg.get("role") == "system": sys_content.append(msg.get("content", ""))
            else: defragged.append(msg)
        if sys_content: defragged.insert(0, {"role": "system", "content": " | ".join(sys_content), "importance": 1.0})
        return defragged

    def _deduplicate_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped, last_hash = [], None
        for msg in messages:
            msg_hash = hash(msg.get("content", ""))
            if msg_hash != last_hash:
                deduped.append(msg)
                last_hash = msg_hash
        return deduped

    def _token_level_pruning(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        stop_words = {" a ", " the ", " is ", " are ", " and ", " of ", " to "}
        for msg in messages:
            if msg.get("importance", 0.5) < 0.8:
                content = msg.get("content", "")
                for word in stop_words: content = content.replace(word, " ")
                msg["content"] = re.sub(r'\s+', ' ', content).strip()
        return messages

    def _swap_to_disk(self, message: Dict[str, Any]):
        with open(self.swap_file, "a") as f: f.write(json.dumps(message) + "\n")

    def _compress_messages(self, messages: List[Dict[str, Any]], target_vram: float) -> List[Dict[str, Any]]:
        compressed = messages[:]
        while len(compressed) > 2:
            total_chars = sum(len(m.get("content", "")) for m in compressed)
            if (total_chars * 10) / self.bytes_per_mb <= target_vram: break
            idx_to_remove, min_importance = -1, float('inf')
            for i in range(1, len(compressed)):
                imp = compressed[i].get("importance", 0.5)
                if imp < min_importance: min_importance, idx_to_remove = imp, i
            if idx_to_remove != -1:
                self._swap_to_disk(compressed[idx_to_remove])
                compressed.pop(idx_to_remove)
            else: break
        if len(compressed) < len(messages): compressed.insert(1, {"role": "system", "content": "[CONTEXT COMPRESSED]", "importance": 0.9})
        return compressed
