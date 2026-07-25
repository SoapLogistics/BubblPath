import pytest
from solomon_abstract_reasoning import FractalOntologySynthesizer
import math

def test_infinite_learning_synthesis():
    synth = FractalOntologySynthesizer(dimensions=3, max_concepts=50)

    # Pre-train
    synth.learn_concept("compression", "algorithms", vector_override=(1.0, 0.5, 0.2))
    synth.learn_concept("lossless", "algorithms", vector_override=(0.9, 0.4, 0.1))

    synth.learn_concept("time_travel", "physics", vector_override=(-0.5, 0.8, -0.9))
    synth.learn_concept("wormhole", "physics", vector_override=(-0.6, 0.7, -0.8))

    synth.learn_concept("infinite_learning", "ai", vector_override=(0.1, 0.9, 0.5))
    synth.learn_concept("recursive_optimization", "ai", vector_override=(0.2, 0.8, 0.6))

    # Try crossing from algorithms to AI
    res = synth.synthesize_cross_domain_leap("compression", "algorithms", "ai")

    assert res["source_concept"] == "compression"
    assert res["source_domain"] == "algorithms"
    assert res["target_domain"] == "ai"

    # Cross from physics to AI
    res2 = synth.synthesize_cross_domain_leap("time_travel", "physics", "ai")

    assert res2["source_concept"] == "time_travel"
    assert res2["source_domain"] == "physics"
    assert res2["target_domain"] == "ai"
    assert len(res2["nearest_target_anchors"]) > 0
