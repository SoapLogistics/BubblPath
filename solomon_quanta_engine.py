"""
The Quanta Engine (solomon_quanta_engine.py)
--------------------------------------------
Implements extreme ternary quantization [-1, 0, 1] for neural representations
and memory embeddings to radically minimize footprint while retaining semantic
routing capabilities. Uses pure Python to maintain absolute portability and zero bloat.
"""

from typing import List, Tuple
import math

Vector = Tuple[float, ...]
TernaryVector = Tuple[int, ...]

class QuantaEngine:
    def __init__(self, threshold: float = 0.1):
        """
        threshold: The magnitude below which a float is compressed to 0.
        Magnitudes above threshold are compressed to -1 or 1 based on sign.
        """
        self.threshold = threshold

    def compress_to_ternary(self, dense_vector: Vector) -> TernaryVector:
        """
        Compresses a high-precision float vector into a sparse ternary format [-1, 0, 1].
        """
        compressed = []
        for val in dense_vector:
            if abs(val) < self.threshold:
                compressed.append(0)
            elif val > 0:
                compressed.append(1)
            else:
                compressed.append(-1)
        return tuple(compressed)

    def decompress_to_dense(self, ternary_vector: TernaryVector, scale: float = 1.0) -> Vector:
        """
        Reconstructs a dense vector from ternary, scaling it by an estimated factor.
        """
        return tuple(val * scale for val in ternary_vector)

    def cosine_similarity(self, v1: TernaryVector, v2: TernaryVector) -> float:
        """
        Calculates cosine similarity directly on ternary vectors for extreme O(1)-like speed.
        (Since values are only -1, 0, 1, math simplifies greatly).
        """
        dot_product = sum(a * b for a, b in zip(v1, v2))

        # Magnitude is just the square root of the count of non-zero elements
        mag1 = math.sqrt(sum(1 for a in v1 if a != 0))
        mag2 = math.sqrt(sum(1 for b in v2 if b != 0))

        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def route_quantum_state(self, state: TernaryVector, memory_bank: List[Tuple[str, TernaryVector]]) -> str:
        """
        Finds the most semantically similar memory trace purely in the quantized domain.
        """
        best_match = None
        best_score = -1.0

        for name, mem_vector in memory_bank:
            score = self.cosine_similarity(state, mem_vector)
            if score > best_score:
                best_score = score
                best_match = name

        return best_match if best_match else "unknown"
