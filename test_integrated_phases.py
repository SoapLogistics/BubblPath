import pytest
from solomon_abstract_reasoning import FractalOntologySynthesizer

def test_context_shadows():
    synth = FractalOntologySynthesizer(dimensions=10)
    synth.learn_concept("API_Route", "backend")

    # Apply phase 4 context bridging
    synth.add_context_shadow("API_Route", '{"url": "/api/users", "method": "GET"}')
    assert "API_Route" in synth.context_shadows
    assert len(synth.context_shadows["API_Route"]) == 10

def test_quantum_integration():
    synth = FractalOntologySynthesizer(dimensions=10)

    synth.establish_quantum_concept("Schrodinger", {"physics": 0.5, "mythology": 0.5})
    assert "Schrodinger" in synth.quantum_registry

    # Observe it to force collapse
    domain = synth.observe_quantum_concept("Schrodinger")
    assert domain in ["physics", "mythology"]

    # Ensure it mathematically exists in the standard matrix now
    assert "Schrodinger" in synth.concepts

def test_holographic_integration():
    synth = FractalOntologySynthesizer(dimensions=4)
    synth.learn_concept("A", "dom", vector_override=(1.0, 0.0, 0.0, 0.0), quantize=False)
    synth.learn_concept("B", "dom", vector_override=(0.0, 1.0, 0.0, 0.0), quantize=False)

    cluster_name, vec = synth.synthesize_holographic_cluster(["A", "B"])
    assert cluster_name.startswith("holo_cluster::")
    assert len(vec) == 4
    # Ensure it's saved in standard memory
    assert cluster_name in synth.concepts
