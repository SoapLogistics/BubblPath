import hashlib
import logging
import math
import os
import re

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger("semantic_embedder")


class SemanticEmbedder:
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def _generate_hash_vector(self, text: str) -> list[float]:
        """
        Fallback feature hashing vectorizer (Hashing Trick) in pure Python.
        Deterministic, fixed-dimension, normalized frequency representation.
        """
        # Tokenize text
        words = [w.lower() for w in re.findall(r"\w+", text)]
        if not words:
            return [0.0] * self.dimension

        vector = [0.0] * self.dimension
        for word in words:
            # Use md5 to deterministically hash word to index in range [0, dimension - 1]
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            vector[idx] += 1.0

        # L2 Normalize the vector
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0.0:
            vector = [v / magnitude for v in vector]

        return vector

    def get_embedding(self, text: str) -> list[float]:
        """
        Retrieves embedding. Uses OpenAI API if configured and available,
        otherwise falls back to deterministic feature hashing vectorizer.
        """
        if not text or not text.strip():
            return [0.0] * self.dimension

        if self.api_key and openai is not None:
            try:
                # Support newer openai>=1.0.0 client if possible, or fallback to legacy
                if hasattr(openai, "OpenAI"):
                    client = openai.OpenAI(api_key=self.api_key)
                    response = client.embeddings.create(
                        input=[text],
                        model="text-embedding-3-small"
                    )
                    # text-embedding-3-small has 1536 dims
                    return response.data[0].embedding
                else:
                    response = openai.Embedding.create(
                        input=[text],
                        model="text-embedding-ada-002"
                    )
                    return response["data"][0]["embedding"]
            except Exception as e:  # noqa: BLE001
                # Log error and fallback gracefully to avoid service disruption
                logger.error(f"[SemanticEmbedder] OpenAI API error: {e}. Falling back to deterministic hashing vector.")

        return self._generate_hash_vector(text)

    def cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Computes cosine similarity between two numeric lists."""
        if len(vec_a) != len(vec_b) or not vec_a or not vec_b:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))

        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0

        return dot_product / (mag_a * mag_b)
