import math
import random
from typing import Dict, List, Tuple, Any
from collections import OrderedDict

# Fast immutable vector using pure Python tuples
Vector = Tuple[float, ...]

def quantize_to_ternary(v: Vector, threshold: float = 0.3) -> Vector:
    """
    Compresses a float vector into a ternary representation (-1.0, 0.0, 1.0)
    using a threshold. Extreme memory and computational efficiency.
    """
    return tuple(1.0 if val > threshold else (-1.0 if val < -threshold else 0.0) for val in v)

def vector_add(v1: Vector, v2: Vector) -> Vector:
    return tuple(a + b for a, b in zip(v1, v2))

def vector_sub(v1: Vector, v2: Vector) -> Vector:
    return tuple(a - b for a, b in zip(v1, v2))

def vector_mul(v: Vector, scalar: float) -> Vector:
    return tuple(a * scalar for a in v)

def dot_product(v1: Vector, v2: Vector) -> float:
    return sum(a * b for a, b in zip(v1, v2))

def vector_magnitude(v: Vector) -> float:
    return math.sqrt(dot_product(v, v))

def cosine_similarity(v1: Vector, v2: Vector) -> float:
    mag1 = vector_magnitude(v1)
    mag2 = vector_magnitude(v2)
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product(v1, v2) / (mag1 * mag2)


class ProgressiveAbstractionTree:
    """Legacy tree class representing previous heuristic groupings."""
    pass


class FractalOntologySynthesizer:
    """
    Evolves the ProgressiveAbstractionTree into a mathematical ontology.
    Concepts are mathematically mapped into an n-dimensional space.
    Cross-domain leaps are achieved by shifting topological domains.
    """
    def __init__(self, dimensions: int = 64, max_concepts: int = 10000):
        self.dimensions = dimensions
        self.max_concepts = max_concepts
        self.concepts: OrderedDict[str, Vector] = OrderedDict()
        self.domains: Dict[str, List[str]] = {}

    def _generate_orthogonal_base(self, seed_string: str) -> Vector:
        """Generates a deterministic vector based on string seeding."""
        # Use a local RNG instance to prevent global random state pollution
        rng = random.Random(seed_string)
        vec = []
        for _ in range(self.dimensions):
            val = rng.uniform(-1.0, 1.0)
            vec.append(val)

        t_vec = tuple(vec)
        mag = vector_magnitude(t_vec)
        if mag == 0:
            return tuple([0.0]*self.dimensions)
        return tuple(v / mag for v in t_vec)

    def learn_concept(self, concept_name: str, domain: str, vector_override: Vector = None, quantize: bool = True) -> None:
        """
        Learn a new concept in a specific domain.
        Mathematically map the abstraction. Optionally applies extreme ternary quantization.
        """
        if vector_override:
            vec = vector_override
        else:
            vec = self._generate_orthogonal_base(f"{domain}::{concept_name}")

        if quantize:
            vec = quantize_to_ternary(vec)

        # LRU cache behavior
        if concept_name in self.concepts:
            del self.concepts[concept_name]
        self.concepts[concept_name] = vec
        if len(self.concepts) > self.max_concepts:
            popped_concept, _ = self.concepts.popitem(last=False)
            # Remove from domains as well
            for d, concepts in self.domains.items():
                if popped_concept in concepts:
                    concepts.remove(popped_concept)

        if domain not in self.domains:
            self.domains[domain] = []
        if concept_name not in self.domains[domain]:
            self.domains[domain].append(concept_name)

    def get_domain_centroid(self, domain: str) -> Vector:
        """Calculate the centroid (mean vector) of a domain based on its concepts."""
        if domain not in self.domains or not self.domains[domain]:
            return tuple([0.0] * self.dimensions)

        sum_vec = tuple([0.0] * self.dimensions)
        for concept in self.domains[domain]:
            sum_vec = vector_add(sum_vec, self.concepts[concept])

        return vector_mul(sum_vec, 1.0 / len(self.domains[domain]))

    def synthesize_cross_domain_leap(self, source_concept: str, source_domain: str, target_domain: str) -> Dict[str, Any]:
        """
        Mathematically map an abstraction and force it into another domain.
        Operation: Target_Space = Source_Concept - Source_Centroid + Target_Centroid
        """
        if source_concept not in self.concepts:
            raise ValueError(f"Concept '{source_concept}' not found in memory.")

        src_centroid = self.get_domain_centroid(source_domain)
        tgt_centroid = self.get_domain_centroid(target_domain)

        # Abstract the concept by removing its source domain's local gravity
        abstracted_concept = vector_sub(self.concepts[source_concept], src_centroid)

        # Project the abstraction into the target domain space
        projected_concept = vector_add(abstracted_concept, tgt_centroid)

        # Find nearest existing concepts to ground the projection in the target domain
        nearest = self.find_nearest_concepts(projected_concept, domain_filter=target_domain, exclude=[source_concept], top_k=3)

        # Quantize the synthesized result for maximum efficiency moving forward
        quantized_projection = quantize_to_ternary(projected_concept)

        return {
            "source_concept": source_concept,
            "source_domain": source_domain,
            "target_domain": target_domain,
            "projected_vector": quantized_projection,
            "raw_projected_vector": projected_concept,
            "nearest_target_anchors": nearest,
            "synthesis_insight": (
                f"Applying abstract topology of '{source_concept}' onto '{target_domain}' "
                f"leveraging proximity to {', '.join([n[0] for n in nearest]) if nearest else 'unmapped territory'}."
            )
        }

    def run_infinite_learning_cycle(self, iterations: int = 1) -> List[Dict[str, Any]]:
        """
        Autonomously selects concepts and synthesizes cross-domain leaps.
        Permanently learns the synthesized hybrid concepts, endlessly expanding capability.
        """
        insights = []
        domain_list = list(self.domains.keys())

        if len(domain_list) < 2:
            return [{"error": "Infinite learning requires at least two populated domains."}]

        for _ in range(iterations):
            # 1. Select random source and target domains
            src_domain, tgt_domain = random.sample(domain_list, 2)

            # 2. Select random concept from source domain
            if not self.domains[src_domain]:
                continue
            src_concept = random.choice(self.domains[src_domain])

            # 3. Perform Synthesis Leap
            try:
                leap_data = self.synthesize_cross_domain_leap(src_concept, src_domain, tgt_domain)

                # 4. Integrate new hybrid concept permanently into memory graph
                new_concept_name = f"hybrid::{src_concept}_applied_to_{tgt_domain}"

                # We learn this new concept into an 'invention' domain
                invention_domain = f"invention::{tgt_domain}"

                self.learn_concept(
                    concept_name=new_concept_name,
                    domain=invention_domain,
                    vector_override=leap_data["projected_vector"], # Already quantized
                    quantize=False # It is already ternary
                )

                insights.append({
                    "new_concept": new_concept_name,
                    "invention_domain": invention_domain,
                    "insight": leap_data["synthesis_insight"]
                })
            except Exception as e:
                # Catch math errors (e.g., zero magnitude centroids) on early topologies
                pass

        return insights

    def find_nearest_concepts(self, target_vector: Vector, domain_filter: str = None, exclude: List[str] = None, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find concepts closest to the given vector using cosine similarity (O(1) semantic search cache)."""
        exclude = exclude or []

        allowed_concepts = None
        if domain_filter and domain_filter in self.domains:
            allowed_concepts = set(self.domains[domain_filter])

        similarities = []
        for name, vec in self.concepts.items():
            if name in exclude:
                continue
            if allowed_concepts is not None and name not in allowed_concepts:
                continue

            sim = cosine_similarity(target_vector, vec)
            similarities.append((name, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
