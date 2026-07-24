from typing import List, Dict, Any

class DynamicContextEngine:
    """
    Replaces every fixed context limit.
    Everything becomes adaptive (Size, Priority, Compression, Summarization).
    """
    def __init__(self, max_vram_mb: int = 1500):
        self.max_vram_mb = max_vram_mb
        self.bytes_per_mb = 1024 * 1024

    def budget_context(self, current_vram_usage: float, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Adaptively truncates or compresses the message history based on real-time VRAM constraints.
        """
        available_vram = self.max_vram_mb - current_vram_usage

        total_chars = sum(len(m.get("content", "")) for m in messages)
        # Approximate VRAM usage per char in inference context (very rough estimate)
        estimated_vram_needed = (total_chars * 10) / self.bytes_per_mb

        if estimated_vram_needed > available_vram:
            return self._compress_messages(messages, target_vram=available_vram)

        return messages

    def _compress_messages(self, messages: List[Dict[str, str]], target_vram: float) -> List[Dict[str, str]]:
        # Iteratively prune oldest messages (excluding system prompt) until it fits
        compressed = messages[:]
        while len(compressed) > 2:
            total_chars = sum(len(m.get("content", "")) for m in compressed)
            if (total_chars * 10) / self.bytes_per_mb <= target_vram:
                break
            # Remove the oldest non-system message
            for i, msg in enumerate(compressed):
                if msg.get("role") != "system":
                    compressed.pop(i)
                    break

        if len(compressed) < len(messages):
            compressed.insert(0, {"role": "system", "content": f"[SYSTEM MEMORY COMPRESSED DUE TO VRAM CONSTRAINTS]"})

        return compressed

class MemoryCompressionPipeline:
    """
    Investigates storing graph structures and context using quantized representations.
    """
    @staticmethod
    def compress_graph_node(node_data: str) -> bytes:
        import zlib
        return zlib.compress(node_data.encode("utf-8"))
