import os
import hashlib
import json
import math
from typing import List, Dict, Any, Optional

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class SemanticEmbedder:
    """
    Handles generation of vector embeddings for Knowledge Cards.
    Uses OpenAI's text-embedding-ada-002 if available, otherwise falls back
    to a deterministic local hashing vectorizer for a baseline dense space.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if self.api_key and HAS_OPENAI:
            self.client = OpenAI(api_key=self.api_key)
            self.use_openai = True
        else:
            self.use_openai = False

    def _local_hash_embedding(self, text: str, dimensions: int = 128) -> List[float]:
        """
        Creates a deterministic local embedding using SHA-256 chunk hashing.
        This provides a dense vector space fallback without external APIs.
        """
        if not text:
            return [0.0] * dimensions

        # Normalize text
        text = text.lower().strip()

        vector = []
        chunk_size = max(1, len(text) // dimensions)

        for i in range(dimensions):
            start = i * chunk_size
            end = start + chunk_size if i < dimensions - 1 else len(text)
            chunk = text[start:end]

            # Hash chunk to a float between -1.0 and 1.0
            hash_val = int(hashlib.sha256(chunk.encode('utf-8')).hexdigest()[:8], 16)
            normalized_val = (hash_val / 0xffffffff) * 2 - 1
            vector.append(normalized_val)

        # L2 Normalize
        magnitude = math.sqrt(sum(x*x for x in vector))
        if magnitude > 0:
            return [x / magnitude for x in vector]
        return vector

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a dense embedding for the given text."""
        if self.use_openai:
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"OpenAI Embedding failed: {e}. Falling back to local hash vectorizer.")
                return self._local_hash_embedding(text)
        else:
            return self._local_hash_embedding(text)

    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Computes cosine similarity between two embeddings with division-by-zero protection."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        sim = dot_product / (mag1 * mag2)
        # Clip bounds to [-1.0, 1.0] for floating point drift
        return max(min(sim, 1.0), -1.0)
