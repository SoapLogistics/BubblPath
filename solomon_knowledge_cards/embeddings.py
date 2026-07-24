import os
import re
import math
import hashlib
from typing import List, Optional

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
