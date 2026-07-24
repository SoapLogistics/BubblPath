import pytest
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_embeddings import DenseEmbeddingProvider, DeterministicHashProvider
import os

def test_retrieval_quality_comparison():
    # Setup test DBs
    if os.path.exists("test_dense.db"):
        os.remove("test_dense.db")
    if os.path.exists("test_hash.db"):
        os.remove("test_hash.db")

    db_dense = SolomonMnemosyneDB("test_dense.db", embedding_provider=DenseEmbeddingProvider())
    db_hash = SolomonMnemosyneDB("test_hash.db", embedding_provider=DeterministicHashProvider())

    cards = [
        ("C1", "math", "geometry", "The Pythagorean theorem relates the sides of a right triangle."),
        ("C2", "science", "physics", "Newton's second law states force equals mass times acceleration."),
        ("C3", "history", "rome", "Julius Caesar was assassinated on the Ides of March."),
        ("C4", "math", "algebra", "The quadratic formula solves polynomials of degree two.")
    ]

    for c in cards:
        db_dense.upsert_card(*c)
        db_hash.upsert_card(*c)

    query = "How do I calculate the hypotenuse?"

    dense_results = db_dense.semantic_search(query, top_k=2)
    hash_results = db_hash.semantic_search(query, top_k=2)

    # Evaluate Quality
    print("Dense Results:", [r["card_id"] for r in dense_results])
    print("Hash Results:", [r["card_id"] for r in hash_results])

    # The dense model should correctly identify geometry (C1) as the top hit
    assert dense_results[0]["card_id"] == "C1" or dense_results[1]["card_id"] == "C1"

    if os.path.exists("test_dense.db"):
        os.remove("test_dense.db")
    if os.path.exists("test_hash.db"):
        os.remove("test_hash.db")

if __name__ == "__main__":
    pytest.main(["-v", "-s", "test_retrieval_quality.py"])
