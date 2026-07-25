import pytest
from solomon_memory.graph.engine import cosine_similarity

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    # Same vector should have similarity 1.0
    assert abs(cosine_similarity(v1, v2) - 1.0) < 1e-6
    # Orthogonal vectors should have similarity 0.0
    assert abs(cosine_similarity(v1, v3) - 0.0) < 1e-6
