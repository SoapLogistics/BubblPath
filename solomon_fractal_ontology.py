import math
from typing import Tuple, List, Dict

# Type alias for our pure Python mathematical vector representations
Vector = Tuple[float, ...]

class FractalOntologySynthesizer:
    """
    Fractal Ontology Synthesizer.
    Leverages pure Python, zero-dependency mathematical vector representations
    to map abstract concepts and perform cross-domain analogical leaps via
    domain centroid shifting.
    """
    def __init__(self):
        # A dictionary mapping abstract concept strings to their Vector representation
        self.ontology_graph: Dict[str, Vector] = {}

    def _add_vectors(self, v1: Vector, v2: Vector) -> Vector:
        """Adds two vectors."""
        return tuple(a + b for a, b in zip(v1, v2))

    def _subtract_vectors(self, v1: Vector, v2: Vector) -> Vector:
        """Subtracts v2 from v1."""
        return tuple(a - b for a, b in zip(v1, v2))

    def _scalar_multiply(self, v: Vector, scalar: float) -> Vector:
        """Multiplies a vector by a scalar."""
        return tuple(a * scalar for a in v)

    def _vector_magnitude(self, v: Vector) -> float:
        """Calculates the magnitude of a vector."""
        return math.sqrt(sum(a * a for a in v))

    def _cosine_similarity(self, v1: Vector, v2: Vector) -> float:
        """Calculates cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag_v1 = self._vector_magnitude(v1)
        mag_v2 = self._vector_magnitude(v2)
        if mag_v1 == 0 or mag_v2 == 0:
            return 0.0
        return dot_product / (mag_v1 * mag_v2)

    def add_concept(self, name: str, vector: Vector):
        """Adds or updates a concept in the ontology graph."""
        self.ontology_graph[name] = vector

    def calculate_centroid(self, concept_names: List[str]) -> Vector:
        """Calculates the geometric centroid of a list of concepts."""
        if not concept_names:
            return tuple()

        vectors = [self.ontology_graph[name] for name in concept_names if name in self.ontology_graph]
        if not vectors:
            return tuple()

        dimensions = len(vectors[0])
        centroid = [0.0] * dimensions
        for v in vectors:
            for i in range(dimensions):
                centroid[i] += v[i]

        return tuple(c / len(vectors) for c in centroid)

    def synthesize_analogical_leap(self, source_domain: List[str], target_domain: List[str], source_concept: str) -> str:
        """
        Performs an analogical leap from the source domain to the target domain.
        It calculates the delta between the source concept and its domain centroid,
        and applies that delta to the target domain centroid to find the nearest concept.
        """
        if source_concept not in self.ontology_graph:
            return "Error: Source concept not found."

        source_centroid = self.calculate_centroid(source_domain)
        target_centroid = self.calculate_centroid(target_domain)

        if not source_centroid or not target_centroid:
            return "Error: Invalid domains."

        # Calculate semantic delta: source_concept - source_centroid
        source_vector = self.ontology_graph[source_concept]
        delta_vector = self._subtract_vectors(source_vector, source_centroid)

        # Apply delta to target centroid: target_centroid + delta
        target_leap_vector = self._add_vectors(target_centroid, delta_vector)

        # Find nearest concept in target domain
        best_match = None
        best_similarity = -1.0

        for concept in target_domain:
            if concept in self.ontology_graph:
                similarity = self._cosine_similarity(target_leap_vector, self.ontology_graph[concept])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = concept

        return best_match if best_match else "No match found."
