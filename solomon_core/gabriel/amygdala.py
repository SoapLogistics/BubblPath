import hashlib
import time
from typing import Dict, Tuple, Optional

class AmygdalaRouter:
    """
    Amygdala Routing Protocol.
    Neural Efficiency router that bypasses the LLM for simple, familiar requests (reflex cache)
    via quantized O(1) text hashing. Only calls the LLM (cortex) for genuine novelties,
    injecting calculated emotional tags (e.g., urgency, frustration).
    """
    def __init__(self, max_cache_size: int = 1000):
        self.reflex_cache: Dict[str, Tuple[str, float]] = {} # hash -> (response, timestamp)
        self.max_cache_size = max_cache_size
        self.novelty_threshold = 0.8 # Simulated threshold for novelty

    def _hash_text(self, text: str) -> str:
        """Quantized O(1) text hashing for exact matches."""
        # Simple normalization
        normalized = text.strip().lower()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def _calculate_emotional_tags(self, text: str, user_history_len: int) -> Dict[str, float]:
        """Calculates emotional tags for the LLM prompt injection."""
        urgency = 0.1
        frustration = 0.1

        text_upper = text.upper()
        if "URGENT" in text_upper or "ASAP" in text_upper or "!" in text:
             urgency = 0.8

        if user_history_len > 5: # If they've asked a lot recently, maybe frustrated
            frustration = 0.5
        if "WHY" in text_upper or "BROKEN" in text_upper:
            frustration = 0.9

        return {"urgency": urgency, "frustration": frustration}

    def route_request(self, user_message: str, user_history_len: int = 0) -> Tuple[bool, Optional[str], Dict[str, float]]:
        """
        Routes a request.
        Returns (use_cortex, cached_response, emotional_tags)
        If use_cortex is True, the LLM should be called.
        """
        req_hash = self._hash_text(user_message)

        # 1. Reflex Cache Check (O(1))
        if req_hash in self.reflex_cache:
             cached_resp, timestamp = self.reflex_cache[req_hash]
             # simple TTL check (e.g., 1 hour)
             if time.time() - timestamp < 3600:
                 return False, cached_resp, {}
             else:
                 del self.reflex_cache[req_hash]

        # 2. Cortex Routing (LLM)
        emotional_tags = self._calculate_emotional_tags(user_message, user_history_len)
        return True, None, emotional_tags

    def learn_response(self, user_message: str, response: str):
        """Caches a response for future reflex routing."""
        if len(self.reflex_cache) >= self.max_cache_size:
            # Simple eviction: clear 10%
            keys_to_delete = list(self.reflex_cache.keys())[:int(self.max_cache_size * 0.1)]
            for k in keys_to_delete:
                del self.reflex_cache[k]

        req_hash = self._hash_text(user_message)
        self.reflex_cache[req_hash] = (response, time.time())
