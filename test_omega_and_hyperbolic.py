import pytest
from solomon_abstract_reasoning import FractalOntologySynthesizer

def test_omega_function():
    synth = FractalOntologySynthesizer(dimensions=4)
    # The God node is (0,0,0,0).
    # Learn a concept near God node
    synth.learn_concept("Math", "science", vector_override=(0.1, 0.1, 0.0, 0.0), quantize=False)

    metrics = synth.calculate_omega_truth("Math")
    assert "omega_value" in metrics
    assert "domain_density" in metrics
    assert "distance_to_god_node" in metrics

    # Distance to God Node should be calculated correctly
    # sqrt(0.1^2 + 0.1^2) = sqrt(0.02) = ~0.1414
    assert 0.14 <= metrics["distance_to_god_node"] <= 0.15

def test_hyperbolic_routing():
    synth = FractalOntologySynthesizer(dimensions=3)
    # Flat space (<= 5 concepts in domain)
    synth.learn_concept("A", "dom", vector_override=(1.0, 0.0, 0.0), quantize=False)
    synth.learn_concept("B", "dom", vector_override=(-1.0, 0.0, 0.0), quantize=False)

    target = (0.9, 0.0, 0.0)

    # Standard Euclidean test via auto-router (flat space)
    standard_res = synth.find_nearest_concepts(target, domain_filter="dom")
    assert standard_res[0][0] == "A"

    # Push into Curved space (> 5 concepts in domain)
    synth.learn_concept("C", "dom", quantize=False)
    synth.learn_concept("D", "dom", quantize=False)
    synth.learn_concept("E", "dom", quantize=False)
    synth.learn_concept("F", "dom", quantize=False)

    # Hyperbolic test via auto-router (curved space threshold crossed)
    hyperbolic_res = synth.find_nearest_concepts(target, domain_filter="dom")
    # Ensure it successfully executes and returns A as nearest based on inverted distance mapping
    assert hyperbolic_res[0][0] == "A"
