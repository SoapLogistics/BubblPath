import pytest
from solomon_abstract_reasoning import (
    quantize_to_ternary,
    dequantize_from_ternary,
    bitwise_ternary_similarity
)
import math

def test_ternary_quantization_bitwise_packing():
    # Test vector of size 8
    raw_vector = (1.0, -1.0, 0.0, 1.0, -1.0, 0.0, 0.0, 0.0)
    pos_mask, neg_mask = quantize_to_ternary(raw_vector, threshold=0.3)

    # Indices with 1.0: 0, 3 (binary 1001 = 9)
    assert pos_mask == 9

    # Indices with -1.0: 1, 4 (binary 10010 = 18)
    assert neg_mask == 18

def test_dequantization():
    packed = (9, 18) # From previous test
    dimensions = 8
    expanded = dequantize_from_ternary(packed, dimensions)

    assert expanded == (1.0, -1.0, 0.0, 1.0, -1.0, 0.0, 0.0, 0.0)

def test_bitwise_similarity():
    # v1: (1, 1, 0, -1) -> pos: 3 (0011), neg: 8 (1000)
    t1 = (3, 8)

    # v2 matches v1 exactly
    t2 = (3, 8)
    assert bitwise_ternary_similarity(t1, t2, dimensions=4) == 1.0

    # v3 is completely orthogonal/empty -> returns 0
    t3 = (0, 0)
    assert bitwise_ternary_similarity(t1, t3, dimensions=4) == 0.0

    # v4 is complete opposite -> returns -1
    # v4: (-1, -1, 0, 1) -> pos: 8, neg: 3
    t4 = (8, 3)
    assert bitwise_ternary_similarity(t1, t4, dimensions=4) == -1.0
