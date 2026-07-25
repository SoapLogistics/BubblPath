"""
The Fractal Ontology Synthesizer (solomon_abstract_reasoning.py)
----------------------------------------------------------------
Implements pure Python, zero-dependency mathematical vector representations
to map abstract concepts and perform cross-domain analogical capability leaps
using domain centroid shifting.
"""

import math
from typing import List, Tuple, Dict, Optional

Vector = Tuple[float, ...]

class FractalOntologySynthesizer:
    def __init__(self):
        # A registry mapping domain names to a list of concept vectors (tuples)
        self.domains: Dict[str, Dict[str, Vector]] = {}

    def add_domain_concept(self, domain: str, concept_name: str, vector: Vector):
        """Adds a concept vector to a specific domain."""
        if domain not in self.domains:
            self.domains[domain] = {}
        self.domains[domain][concept_name] = vector

    def _add_vectors(self, v1: Vector, v2: Vector) -> Vector:
        return tuple(a + b for a, b in zip(v1, v2))

    def _sub_vectors(self, v1: Vector, v2: Vector) -> Vector:
        return tuple(a - b for a, b in zip(v1, v2))

    def _scale_vector(self, v: Vector, scalar: float) -> Vector:
        return tuple(a * scalar for a in v)

    def _distance(self, v1: Vector, v2: Vector) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def calculate_centroid(self, domain: str) -> Optional[Vector]:
        """Calculates the geometric center (centroid) of a domain."""
        if domain not in self.domains or not self.domains[domain]:
            return None

        concepts = list(self.domains[domain].values())
        dimensions = len(concepts[0])
        centroid = [0.0] * dimensions

        for v in concepts:
            for i, val in enumerate(v):
                centroid[i] += val

        return tuple(val / len(concepts) for val in centroid)

    def synthesize_capability_leap(self, source_domain: str, target_domain: str, capability_vector: Vector) -> Optional[Dict]:
        """
        Performs an analogical capability leap by applying the translation vector
        (Target Centroid - Source Centroid) to the source capability.
        Returns the new synthesized vector and the closest matching concept in the target domain.
        """
        source_centroid = self.calculate_centroid(source_domain)
        target_centroid = self.calculate_centroid(target_domain)

        if not source_centroid or not target_centroid:
            return None

        if len(source_centroid) != len(target_centroid) or len(source_centroid) != len(capability_vector):
            raise ValueError("All domains and capabilities must have the same dimensionality.")

        # Translation vector representing the semantic shift between domains
        shift_vector = self._sub_vectors(target_centroid, source_centroid)

        # The new capability in the target domain's space
        synthesized_vector = self._add_vectors(capability_vector, shift_vector)

        # Find nearest neighbor in target domain to ground the synthesized concept
        closest_concept = None
        min_dist = float('inf')

        for name, v in self.domains[target_domain].items():
            dist = self._distance(synthesized_vector, v)
            if dist < min_dist:
                min_dist = dist
                closest_concept = name

        return {
            "synthesized_vector": synthesized_vector,
            "closest_grounded_concept": closest_concept,
            "distance": min_dist
        }
