from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import hashlib
import math
import datetime

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        pass

class DeterministicHashProvider(EmbeddingProvider):
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            dimensions = 128
            vector = [0.0] * dimensions

            raw_words = text.lower().replace(",", " ").replace(".", " ").split()
            stopwords = {"the", "and", "is", "a", "an", "of", "to", "in", "for", "with", "on", "at"}
            words = [w for w in raw_words if w not in stopwords]
            if not words:
                vector[0] = 1.0
                embeddings.append(vector)
                continue

            for word in words:
                h = hashlib.sha256(word.encode("utf-8")).hexdigest()
                for i in range(3):
                    part = h[i*8:(i+1)*8]
                    if part:
                        idx = int(part, 16) % dimensions
                        val = (int(h[(i+1)*8:(i+2)*8], 16) % 100) / 100.0 if idx < dimensions - 1 else 0.5
                        vector[idx] += val

            sq_sum = sum(x ** 2 for x in vector)
            norm = math.sqrt(sq_sum)

            if norm < 1e-9:
                vector[0] = 1.0
                embeddings.append(vector)
            else:
                embeddings.append([float(x / norm) for x in vector])
        return embeddings

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "provider": "deterministic_hash",
            "model": "sha256_fallback",
            "vector_dimension": 128,
            "model_fingerprint": "v1.0",
            "confidence_classification": "degraded_fallback"
        }

class DenseEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            print(f"Warning: sentence-transformers not installed. {self.model_name} cannot be loaded.")
            self.model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.model is None:
            return DeterministicHashProvider().embed_texts(texts)

        # sentence-transformers outputs NumPy arrays, we convert to standard Python float lists
        embeddings = self.model.encode(texts)
        return [list(map(float, emb)) for emb in embeddings]

    def get_metadata(self) -> Dict[str, Any]:
        if self.model is None:
            return DeterministicHashProvider().get_metadata()

        return {
            "provider": "sentence_transformers",
            "model": self.model_name,
            "vector_dimension": self.model.get_embedding_dimension() if hasattr(self.model, 'get_embedding_dimension') else 384,
            "model_fingerprint": "verified_local",
            "confidence_classification": "high_confidence_dense"
        }
