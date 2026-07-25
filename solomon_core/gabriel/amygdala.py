import re
import hashlib
import time

class AmygdalaRouter:
    """
    The Amygdala Routing Protocol (Neural Efficiency).

    Simulates a biological Amygdala to determine whether a cognitive task can be
    handled by a localized, hyper-efficient reflex (quantized cached function)
    or requires waking up the Cortex (expensive LLM).

    This pushes the boundary of efficiency by treating LLM calls not as the default,
    but as a costly conscious effort only triggered by genuine novelty or high complexity.
    """

    def __init__(self):
        # The reflex cache: maps quantized hashes to (response, hit_count)
        # In a 20-year lifespan, this could be backed by SQLite/MemoryMap,
        # but for ultimate speed, it's an in-memory dictionary.
        self._reflex_arc = {}

        # Simple heuristic dictionaries for ultra-fast O(1) emotional tagging
        self._urgency_triggers = {"urgent", "asap", "quick", "fast", "now", "immediately", "emergency", "critical", "hurry"}
        self._frustration_triggers = {"angry", "frustrated", "hate", "wtf", "stupid", "broken", "fail", "terrible", "worst", "damn"}
        self._complexity_triggers = {"analyze", "synthesize", "evaluate", "compare", "contrast", "architecture", "design", "explain"}

    def _quantize(self, text: str) -> str:
        """
        Hyper-efficient O(1) text hashing.
        Strips noise, normalizes, and generates a compact hash to serve as a memory key.
        """
        # Normalize: lowercase, remove non-alphanumeric, collapse whitespace
        normalized = re.sub(r'[^a-z0-9]', '', text.lower())
        # Use a fast hash (MD5 is fast enough for internal non-cryptographic routing)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def analyze_tags(self, text: str) -> dict:
        """
        Extracts emotional and cognitive tags from the raw text in microseconds.
        """
        words = set(re.findall(r'\b\w+\b', text.lower()))

        urgency_score = len(words.intersection(self._urgency_triggers)) / max(1, len(self._urgency_triggers))
        frustration_score = len(words.intersection(self._frustration_triggers)) / max(1, len(self._frustration_triggers))
        complexity_score = len(words.intersection(self._complexity_triggers)) / max(1, len(self._complexity_triggers))

        # Determine novelty based on reflex cache presence
        quantized_key = self._quantize(text)
        novelty_score = 0.0 if quantized_key in self._reflex_arc else 1.0

        # High length also implies high complexity/novelty
        if len(text) > 500:
            complexity_score = min(1.0, complexity_score + 0.5)

        return {
            "urgency": min(1.0, urgency_score * 5.0), # Amplified for sensitivity
            "frustration": min(1.0, frustration_score * 5.0),
            "complexity": min(1.0, complexity_score * 3.0),
            "novelty": novelty_score,
            "quantized_key": quantized_key
        }

    def process(self, text: str) -> dict:
        """
        The core routing decision.
        Returns either a 'reflex' bypass or a 'cortex' wake-up call.
        """
        tags = self.analyze_tags(text)
        q_key = tags["quantized_key"]

        # A task is "simple" if it has low complexity and low novelty (we've seen it)
        # If it's a known reflex, we bypass the LLM.
        if q_key in self._reflex_arc and tags["complexity"] < 0.5:
            response, hits = self._reflex_arc[q_key]
            # Update hit count for "myelination" (strengthening the pathway)
            self._reflex_arc[q_key] = (response, hits + 1)

            return {
                "route": "reflex",
                "response": response,
                "tags": tags,
                "metrics": {"time_saved_ms": 1500, "energy_saved": "high"} # Theoretical metrics
            }

        # Otherwise, wake up the Cortex (LLM)
        return {
            "route": "cortex",
            "tags": tags
        }

    def learn(self, text: str, response: str, force: bool = False):
        """
        Myelination process: if a response is successful and the input is simple,
        we cache it in the reflex arc so the LLM is never needed for it again.
        """
        tags = self.analyze_tags(text)

        # Only learn low-complexity things unless forced
        if force or tags["complexity"] < 0.5:
            q_key = self._quantize(text)
            # Initialize with 1 hit
            self._reflex_arc[q_key] = (response, 1)
            return True
        return False
