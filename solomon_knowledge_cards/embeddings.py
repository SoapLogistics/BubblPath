import os
import re
import math
import hashlib
from typing import List, Optional, Dict, Any

try:
    import openai
except ImportError:
    openai = None

# Semantic Concept Anchors for 384-dimensional Dense Concept Projector
CONCEPT_ANCHORS = {
    "system_core": ["system", "compiler", "core", "runtime", "virtualenv", "daemon", "cleanup", "process", "thread"],
    "database": ["database", "sqlite", "table", "migration", "query", "sql", "persist", "schema", "record", "transaction"],
    "security": ["security", "auth", "bearer", "token", "classification", "clearance", "restricted", "compliance", "encryption"],
    "sports_betting": ["sports", "odds", "betting", "picks", "bookmaker", "shin", "kelly", "stake", "arbitrage", "profit", "bankroll"],
    "testing": ["testing", "pytest", "assertion", "test", "coverage", "mock", "fixture", "rollback", "compile", "failed"],
    "ai_models": ["model", "llm", "quantization", "ampba", "ollama", "gpt", "openai", "embeddings", "weights", "inference"],
    "network": ["network", "proxy", "port", "tailscale", "comms", "route", "gateway", "latency", "socket", "unreachable"],
    "planning": ["planning", "prometheus", "checklist", "graph", "relation", "dependency", "safeguard", "step", "autonomous"]
}

class SemanticEmbedder:
    """
    Lightweight, advanced semantic vector embedding adapter.
    Bridges FTS search with pure-Python Concept Projection vectorizer (128-dim) or OpenAI embeddings.
    """
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def _generate_concept_vector(self, text: str) -> List[float]:
        """
        Pure-Python Dense Latent Semantic Concept Projector.
        Projects text into a 384-dimensional semantic concept space using vocabulary anchors.
        """
        words = [w.lower() for w in re.findall(r'\w+', text or "")]
        if not words:
            return [0.0] * self.dimension

        # We have 8 concept axes. Each axis gets 48 slots in our 384-dimensional vector.
        axis_keys = list(CONCEPT_ANCHORS.keys())
        slots_per_axis = self.dimension // len(axis_keys) # 384 // 8 = 48 slots

        vector = [0.0] * self.dimension

        for word in words:
            # 1. Calculate semantic affinity to each of the 8 concept axes
            for axis_idx, axis in enumerate(axis_keys):
                anchors = CONCEPT_ANCHORS[axis]

                # Check for direct or partial match
                affinity = 0.0
                for anchor in anchors:
                    if word == anchor:
                        affinity += 2.0
                    elif anchor in word or word in anchor:
                        affinity += 0.8

                if affinity > 0.0:
                    # Project this word into the 48-slot subspace allocated to this axis
                    # We use a deterministic hash of the word to find the exact slot index in this subspace
                    h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
                    slot_offset = h % slots_per_axis
                    vector_idx = (axis_idx * slots_per_axis) + slot_offset
                    vector[vector_idx] += affinity

            # 2. General fallback background noise projection to distribute terms without direct concept matching
            # This preserves unique identity for words outside the concept vocabulary anchors
            h_fallback = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            fallback_idx = h_fallback % self.dimension
            vector[fallback_idx] += 1.0

        # L2 Normalize the final 384-dimensional vector
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0.0:
            vector = [v / magnitude for v in vector]

        return vector

    def get_embedding(self, text: str) -> List[float]:
        """
        Retrieves embedding vector. Uses OpenAI API if configured and available,
        otherwise falls back to deterministic pure-Python Concept Projector.
        """
        if not text or not text.strip():
            return [0.0] * self.dimension

        if self.api_key and openai is not None:
            try:
                if hasattr(openai, "OpenAI"):
                    client = openai.OpenAI(api_key=self.api_key)
                    response = client.embeddings.create(
                        input=[text],
                        model="text-embedding-3-small"
                    )
                    return response.data[0].embedding
                else:
                    response = openai.Embedding.create(
                        input=[text],
                        model="text-embedding-ada-002"
                    )
                    return response['data'][0]['embedding']
            except Exception:
                # Fallback gracefully to our 384-dimensional concept projection
                pass

        return self._generate_concept_vector(text)

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Computes cosine similarity between two numeric lists with full safeguards."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))

        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0

        sim = dot_product / (mag_a * mag_b)
        return max(-1.0, min(1.0, sim))


class RAGVectorCompressor:
    """SOSS Phase 21 RAG Semantic Vector Compressor."""
    def __init__(self):
        pass

    def compress_vector_to_1bit(self, vector: List[float]) -> List[int]:
        """
        Compresses a high-dimensional dense concept vector into a 1-bit sign configuration
        representing dimensions as either -1 or +1 to shrink RAM footprint.
        """
        if not vector:
            return []
        # Quantize components: +1 if component >= 0.0 else -1
        return [1 if val >= 0.0 else -1 for val in vector]

    def estimate_compression_savings(self, initial_vector_count: int, dimension: int = 128) -> Dict[str, Any]:
        """Calculates expected index footprint reductions on memory and storage."""
        # Dense float requires 4 bytes per dimension
        initial_bytes = initial_vector_count * dimension * 4
        # Compressed requires 1 bit per dimension -> packed as bits: (dimension / 8) bytes
        compressed_bytes = initial_vector_count * math.ceil(dimension / 8.0)

        savings_ratio = initial_bytes / max(1, compressed_bytes)

        return {
            "vectors_index_count": initial_vector_count,
            "vector_dimensions": dimension,
            "original_dense_size_bytes": initial_bytes,
            "compressed_1bit_size_bytes": compressed_bytes,
            "footprint_reduction_ratio": round(savings_ratio, 2),
            "percentage_saved": f"{round((1.0 - (compressed_bytes / initial_bytes)) * 100, 2)}%" if initial_bytes > 0 else "0%"
        }
