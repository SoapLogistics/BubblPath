import pytest
from core.solomon_knowledge_cards.api.embeddings import SemanticEmbedder

def test_embedder_fallback_hashing():
    embedder = SemanticEmbedder(dimension=128)
    # Ensure OPENAI_API_KEY is clear for this test
    embedder.api_key = None

    vec = embedder.get_embedding("This is a test document.")
    assert len(vec) == 128

    # Should be deterministic
    vec2 = embedder.get_embedding("This is a test document.")
    assert vec == vec2

def test_embedder_cosine_similarity():
    embedder = SemanticEmbedder(dimension=4)
    vec_a = [1.0, 0.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0, 0.0]
    vec_c = [0.0, 1.0, 0.0, 0.0]

    sim = embedder.cosine_similarity(vec_a, vec_b)
    assert sim == 1.0

    sim2 = embedder.cosine_similarity(vec_a, vec_c)
    assert sim2 == 0.0
