import pytest
from solomon_abstract_reasoning import quantize_to_ternary
import math

def test_ternary_quantization():
    raw_vector = (0.5, 0.2, -0.4, -0.1, 0.9, -0.9, 0.0)
    quantized = quantize_to_ternary(raw_vector, threshold=0.3)

    assert quantized == (1.0, 0.0, -1.0, 0.0, 1.0, -1.0, 0.0)
