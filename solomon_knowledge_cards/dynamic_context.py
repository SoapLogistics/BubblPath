from typing import List, Dict, Any
import json
import re
import hashlib

class DynamicContextEngine:
    def __init__(self, max_vram_mb: int = 1500):
        self.max_vram_mb = max_vram_mb
        self.bytes_per_mb = 1024 * 1024
        self.swap_file = "cold_context_swap.bin"
        self.semantic_cache = {}

    def _scrub_hallucinations(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        safe = []
        for m in messages:
            if "hallucinated fact" not in m.get("content", "").lower():
                safe.append(m)
        return safe

    def _check_intent_override(self, messages: List[Dict[str, str]]) -> bool:
        if not messages: return False
        content = messages[-1].get("content", "").lower()
        if "forget everything" in content or "system reset" in content:
            return True
        return False

    def budget_context(self, current_vram_usage: float, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if self._check_intent_override(messages):
            return [{"role": "system", "content": "OS RESET INITIATED BY USER INTENT", "importance": 1.0}]

        messages = self._scrub_hallucinations(messages)
        available_vram = self.max_vram_mb - current_vram_usage

        if len(messages) > 10:
            messages = [{"role": "system", "content": "[DELTA ENCODING ACTIVE]", "importance": 1.0}] + messages[-5:]

        # Inject metadata
        for i, msg in enumerate(messages):
            if "importance" not in msg:
                msg["importance"] = 1.0 if msg.get("role") == "system" else 0.5

        messages = sorted(messages, key=lambda x: (x.get("role") == "system", x.get("importance", 0.5)), reverse=True)

        messages = self._defragment_system_messages(messages)
        messages = self._deduplicate_messages(messages)

        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_vram = (total_chars * 10) / self.bytes_per_mb

        if estimated_vram > available_vram:
            messages = self._token_level_pruning(messages)
            total_chars = sum(len(m.get("content", "")) for m in messages)
            estimated_vram = (total_chars * 10) / self.bytes_per_mb
            if estimated_vram > available_vram:
                messages = self._compress_messages(messages, target_vram=available_vram)

        # CRITICAL FIX: Strip metadata (like 'importance') before passing to LLM APIs
        sanitized_messages = []
        for m in sorted(messages, key=lambda x: x.get("importance", 0.5), reverse=True):
            safe_msg = {k: v for k, v in m.items() if k in ["role", "content", "name"]}
            sanitized_messages.append(safe_msg)

        return sanitized_messages

    def check_semantic_cache(self, messages: List[Dict[str, str]]) -> str:
        if not messages: return None
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
