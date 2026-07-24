import pytest
from solomon_embeddings import DeterministicHashProvider, DenseEmbeddingProvider
import hashlib

def test_deterministic_hash_provider():
    provider = DeterministicHashProvider()

    texts = ["apple", "banana"]
    embeddings = provider.embed_texts(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 128
    assert len(embeddings[1]) == 128

    meta = provider.get_metadata()
    assert meta["provider"] == "deterministic_hash"

def test_dense_embedding_provider_fallback():
    provider = DenseEmbeddingProvider()
    texts = ["apple", "banana"]
    embeddings = provider.embed_texts(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) in (128, 384)

    meta = provider.get_metadata()
    assert meta["provider"] in ("deterministic_hash", "sentence_transformers")

if __name__ == "__main__":
    pytest.main(["-v", "test_embeddings.py"])
