import pytest
import math
from solomon_fractal_advanced import (
    poincare_distance,
    QuantumConcept,
    circular_convolution,
    circular_correlation
)

def test_poincare_distance():
    # Points must be inside the unit disk (magnitude < 1)
    u = (0.5, 0.0)
    v = (-0.5, 0.0)

    # Distance between points symmetrically opposed
    dist1 = poincare_distance(u, v)
    assert dist1 > 0

    # Distance to self is 0
    assert poincare_distance(u, u) == 0.0

    # Points on/outside boundary yield infinity
    x = (1.0, 0.0)
    assert poincare_distance(u, x) == float('inf')

def test_quantum_concept():
    q = QuantumConcept("SchrodingersCat")
    q.add_superposition("alive", 0.5)
    q.add_superposition("dead", 0.5)

    assert q.collapsed_state is None

    # Observe collapses it
    result = q.observe(seed="deterministic_seed")
    assert result in ["alive", "dead"]

    # Second observation remains collapsed
    assert q.observe() == result

    # Can't add states post-collapse
    with pytest.raises(ValueError):
        q.add_superposition("zombie", 1.0)

def test_holographic_compression():
    # Phase 6 HRR Binding math
    v1 = (1.0, 0.5, -0.5, 0.0)
    v2 = (0.0, 1.0, 0.5, -1.0)

    # Bind
    bound = circular_convolution(v1, v2)
    assert len(bound) == 4

    # Unbind (approximate extraction via correlation)
    unbound_v1 = circular_correlation(bound, v2)
    assert len(unbound_v1) == 4

    # In pure HRR, the extracted vector is noisy but highly correlated with the original
    # We verify it doesn't crash and returns the correct dimensions.
