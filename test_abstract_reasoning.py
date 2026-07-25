import pytest
from solomon_abstract_reasoning import (
    FractalOntologySynthesizer,
    vector_add, vector_sub, vector_mul, dot_product, vector_magnitude, cosine_similarity
)
import math

def test_vector_math():
    v1 = (1.0, 2.0, 3.0)
    v2 = (4.0, 5.0, 6.0)

    assert vector_add(v1, v2) == (5.0, 7.0, 9.0)
    assert vector_sub(v2, v1) == (3.0, 3.0, 3.0)
    assert vector_mul(v1, 2.0) == (2.0, 4.0, 6.0)
    assert dot_product(v1, v2) == 4.0 + 10.0 + 18.0
    assert math.isclose(vector_magnitude((3.0, 4.0)), 5.0)

    # Cosine sim of same vector is 1
    assert math.isclose(cosine_similarity(v1, v1), 1.0)
    # Cosine sim of orthogonal vectors is 0
    assert math.isclose(cosine_similarity((1.0, 0.0), (0.0, 1.0)), 0.0)

def test_fractal_ontology_learning_and_centroid():
    synthesizer = FractalOntologySynthesizer(dimensions=4)

    # Override vectors for predictable test math
    synthesizer.learn_concept("modularity", "software", vector_override=(1.0, 0.0, 0.0, 0.0))
    synthesizer.learn_concept("encapsulation", "software", vector_override=(0.0, 1.0, 0.0, 0.0))

    centroid = synthesizer.get_domain_centroid("software")
    assert centroid == (0.5, 0.5, 0.0, 0.0)

    # Empty domain centroid should be zeros
    assert synthesizer.get_domain_centroid("finance") == (0.0, 0.0, 0.0, 0.0)

def test_cross_domain_synthesis():
    synthesizer = FractalOntologySynthesizer(dimensions=3)

    # Domain A: Software (centered around x/y)
    synthesizer.learn_concept("modularity", "software", vector_override=(1.0, 1.0, 0.0))
    synthesizer.learn_concept("DRY", "software", vector_override=(1.0, -1.0, 0.0))
    # Centroid Software: (1.0, 0.0, 0.0)

    # Domain B: Trading (centered around y/z)
    synthesizer.learn_concept("diversification", "trading", vector_override=(0.0, 1.0, 1.0))
    synthesizer.learn_concept("hedging", "trading", vector_override=(0.0, -1.0, 1.0))
    # Centroid Trading: (0.0, 0.0, 1.0)

    # Synthesize leap: Apply 'modularity' from software to trading
    # modularity (1,1,0) - centroid_src (1,0,0) = abstract (0,1,0)
    # abstract (0,1,0) + centroid_tgt (0,0,1) = projected (0,1,1)

    result = synthesizer.synthesize_cross_domain_leap("modularity", "software", "trading")

    projected = result["projected_vector"]
    assert math.isclose(projected[0], 0.0)
    assert math.isclose(projected[1], 1.0)
    assert math.isclose(projected[2], 1.0)

    # The projected vector (0, 1, 1) perfectly matches 'diversification' in trading
    nearest = result["nearest_target_anchors"]
    assert nearest[0][0] == "diversification"
    assert math.isclose(nearest[0][1], 1.0)

def test_deterministic_generation():
    synthesizer = FractalOntologySynthesizer(dimensions=10)
    # Don't quantize for this specific math test since quantization alters the normalized magnitude
    synthesizer.learn_concept("test_concept", "test_domain", quantize=False)

    vec = synthesizer.concepts["test_concept"]
    assert len(vec) == 10
    assert math.isclose(vector_magnitude(vec), 1.0) # Should be normalized
