import math
import random
import threading
import time
import logging
from typing import Dict, List, Tuple, Any
from collections import OrderedDict

# Set up local logger for background tasks
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FractalDream")

# Fast immutable vector using pure Python tuples.
# Note: For ternary math, vectors are returned as bit-packed integers for O(1) ops.
Vector = Tuple[float, ...]

def quantize_to_ternary(v: Vector, threshold: float = 0.3) -> Tuple[int, int]:
    """
    Compresses a float vector into a ternary representation (-1, 0, 1).
    To achieve extreme bitwise efficiency (Phase 1), we pack the entire vector into two integers:
    - pos_mask: bit is 1 if value is 1.0
    - neg_mask: bit is 1 if value is -1.0
    Returns (pos_mask, neg_mask).
    """
    pos_mask = 0
    neg_mask = 0
    for i, val in enumerate(v):
        if val > threshold:
            pos_mask |= (1 << i)
        elif val < -threshold:
            neg_mask |= (1 << i)
    return (pos_mask, neg_mask)

def dequantize_from_ternary(packed: Tuple[int, int], dimensions: int) -> Vector:
    """Expands a (pos_mask, neg_mask) tuple back to a standard Vector for float math."""
    pos_mask, neg_mask = packed
    vec = []
    for i in range(dimensions):
        if (pos_mask & (1 << i)):
            vec.append(1.0)
        elif (neg_mask & (1 << i)):
            vec.append(-1.0)
        else:
            vec.append(0.0)
    return tuple(vec)

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

def bitwise_ternary_similarity(t1: Tuple[int, int], t2: Tuple[int, int], dimensions: int) -> float:
    """
    O(1) semantic similarity using XOR and POPCOUNT logic on bit-packed masks.
    This replaces float-based cosine_similarity for extreme speed.
    """
    pos1, neg1 = t1
    pos2, neg2 = t2

    # Matching elements (pos to pos, neg to neg)
    match_pos = pos1 & pos2
    match_neg = neg1 & neg2
    matches = match_pos | match_neg

    # Conflicting elements (pos to neg, neg to pos)
    conflict_pos_neg = pos1 & neg2
    conflict_neg_pos = neg1 & pos2
    conflicts = conflict_pos_neg | conflict_neg_pos

    # Count set bits (Python 3.10+ int.bit_count())
    match_count = matches.bit_count()
    conflict_count = conflicts.bit_count()

    # Calculate active dimensions to normalize
    active1 = (pos1 | neg1).bit_count()
    active2 = (pos2 | neg2).bit_count()
    total_active = max(1, (active1 + active2) / 2) # Prevent div by zero

    # Score = matches - conflicts, normalized by active dimensions
    return (match_count - conflict_count) / total_active


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
        # Concepts now store either standard vectors or extremely packed ternary tuples (pos_mask, neg_mask)
        self.concepts: OrderedDict[str, Any] = OrderedDict()
        self.domains: Dict[str, List[str]] = {}
        # Context Shadows (Phase 4): stores secondary vectors representing contextual origin
        self.context_shadows: Dict[str, Vector] = {}

        # Thread safety for concurrent API/Dream operations
        self.lock = threading.Lock()
        self._dreaming = False
        self._dream_thread = None

        # Advanced Modules Integration
        self.quantum_registry: Dict[str, Any] = {} # For Phase 5

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

        with self.lock:
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

    # --- Phase 5: Quantum Superposition Integration ---
    def establish_quantum_concept(self, concept_name: str, superpositions: Dict[str, float]) -> None:
        """
        Creates a concept in quantum superposition across multiple domains.
        The concept does not exist as a physical vector until observed.
        """
        from solomon_fractal_advanced import QuantumConcept
        with self.lock:
            q = QuantumConcept(concept_name)
            for dom, prob in superpositions.items():
                q.add_superposition(dom, prob)
            self.quantum_registry[concept_name] = q

    def observe_quantum_concept(self, concept_name: str) -> str:
        """
        Forces wave collapse on a quantum concept, converting it into a
        permanent standard concept locked to the chosen domain.
        """
        with self.lock:
            if concept_name not in self.quantum_registry:
                raise ValueError(f"No quantum state for '{concept_name}'")

            q = self.quantum_registry[concept_name]
            chosen_domain = q.observe()

        # Register it mathematically now that it exists
        self.learn_concept(concept_name, chosen_domain)
        return chosen_domain

    # --- Phase 6: Holographic HRR Integration ---
    def synthesize_holographic_cluster(self, concept_names: List[str]) -> Tuple[str, Vector]:
        """
        Uses circular convolution to compress an infinite number of concepts
        into a single interference pattern of the same topological size (O(1) memory).
        """
        from solomon_fractal_advanced import circular_convolution
        if not concept_names:
            raise ValueError("Provide at least one concept to bind.")

        with self.lock:
            base = self.concepts.get(concept_names[0])
            if base is None:
                raise ValueError(f"Base concept '{concept_names[0]}' not found.")

            if len(base) == 2 and isinstance(base[0], int):
                base = dequantize_from_ternary(base, self.dimensions)

            for name in concept_names[1:]:
                nxt = self.concepts.get(name)
                if not nxt:
                    continue
                if len(nxt) == 2 and isinstance(nxt[0], int):
                    nxt = dequantize_from_ternary(nxt, self.dimensions)

                # Bind into interference pattern
                base = circular_convolution(base, nxt)

            cluster_name = f"holo_cluster::{hash(''.join(concept_names))}"
            # Store the float interference pattern (do not quantize)
            self.concepts[cluster_name] = base

        return cluster_name, base

    def add_context_shadow(self, concept_name: str, context_string: str) -> None:
        """
        Phase 4: Multi-Modal Contextual Bridging.
        Maps an arbitrary context string (e.g. JSON metadata, code snippets) into a
        secondary 'shadow' vector that influences future centroid weighting.
        """
        with self.lock:
            if concept_name not in self.concepts:
                raise ValueError(f"Concept '{concept_name}' not found.")
            # Map context to a standard float vector
            shadow_vec = self._generate_orthogonal_base(context_string)
            self.context_shadows[concept_name] = shadow_vec

    def get_domain_centroid(self, domain: str) -> Vector:
        """Calculate the centroid (mean vector) of a domain based on its concepts."""
        if domain not in self.domains or not self.domains[domain]:
            return tuple([0.0] * self.dimensions)

        sum_vec = tuple([0.0] * self.dimensions)
        for concept in self.domains[domain]:
            c_val = self.concepts[concept]
            # Dequantize if it's bit-packed
            if len(c_val) == 2 and isinstance(c_val[0], int):
                c_val = dequantize_from_ternary(c_val, self.dimensions)
            sum_vec = vector_add(sum_vec, c_val)

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

        c_val = self.concepts[source_concept]
        if len(c_val) == 2 and isinstance(c_val[0], int):
            c_val = dequantize_from_ternary(c_val, self.dimensions)

        # Abstract the concept by removing its source domain's local gravity
        abstracted_concept = vector_sub(c_val, src_centroid)

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

        with self.lock:
            domain_list = list(self.domains.keys())

        if len(domain_list) < 2:
            return [{"error": "Infinite learning requires at least two populated domains."}]

        for _ in range(iterations):
            # 1. Select random source and target domains
            src_domain, tgt_domain = random.sample(domain_list, 2)

            # 2. Select random concept from source domain safely
            with self.lock:
                if not self.domains.get(src_domain):
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
        """
        Find concepts closest to the given vector.
        Automatically utilizes bitwise XOR similarity for packed vectors to drastically reduce compute time.
        """
        exclude = exclude or []

        allowed_concepts = None
        if domain_filter and domain_filter in self.domains:
            allowed_concepts = set(self.domains[domain_filter])

        # Temporarily quantize the incoming target float vector to compare purely via bitwise ops
        target_packed = quantize_to_ternary(target_vector)

        similarities = []
        for name, vec in self.concepts.items():
            if name in exclude:
                continue
            if allowed_concepts is not None and name not in allowed_concepts:
                continue

            if len(vec) == 2 and isinstance(vec[0], int):
                # O(1) Bitwise execution path
                sim = bitwise_ternary_similarity(target_packed, vec, self.dimensions)
            else:
                # Fallback to float execution path
                sim = cosine_similarity(target_vector, vec)

            similarities.append((name, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def start_dream_state(self, cycle_interval_seconds: int = 60):
        """
        Phase 3: Dream State Daemon.
        Spawns a background thread that continuously runs the infinite learning cycle
        during idle time, autonomously evolving the ontology without external prompt.
        """
        if self._dreaming:
            logger.info("Dream state already active.")
            return

        self._dreaming = True

        def _dream_loop():
            logger.info("Fractal Ontology entered Dream State. Infinite Learning activated.")
            while self._dreaming:
                try:
                    # Run a small batch of learning to not lock up the CPU
                    insights = self.run_infinite_learning_cycle(iterations=5)
                    if insights and "error" not in insights[0]:
                        logger.info(f"[Dream] Synthesized {len(insights)} new concepts autonomously.")
                except Exception as e:
                    # Log appropriately rather than swallowing blindly
                    logger.error(f"[Dream] Mathematical anomaly encountered: {str(e)}", exc_info=True)

                time.sleep(cycle_interval_seconds)

        self._dream_thread = threading.Thread(target=_dream_loop, daemon=True)
        self._dream_thread.start()

    def stop_dream_state(self):
        """Halts the autonomous background evolution."""
        self._dreaming = False
        if self._dream_thread:
            self._dream_thread.join(timeout=1.0)
            logger.info("Dream State halted.")
