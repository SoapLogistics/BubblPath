"""
Solomon Perpetual Learning Machine
Phases 26, 27, 29, 30, 31: Watchdogs, Classifiers, and Guardrails

Implements model drift watchdogs, hallucination classifiers, ethical guardrail gates,
tensor refiners, and consensus ballot boxes.
"""

from typing import Dict, List, Any
import math

class ModelDriftWatchdog:
    """
    Measures semantic or parameter representations shift over time.
    """
    def calculate_parameter_drift(self, baseline: List[float], current: List[float]) -> float:
        if len(baseline) != len(current):
            return 1.0 # Maximum drift

        dot = sum(b * c for b, c in zip(baseline, current))
        norm_b = math.sqrt(sum(b ** 2 for b in baseline))
        norm_c = math.sqrt(sum(c ** 2 for c in current))

        denom = norm_b * norm_c
        if denom < 1e-9:
            return 0.0

        similarity = dot / denom
        # Drift ratio = 1 - similarity
        return float(round(max(0.0, 1.0 - similarity), 4))


class HallucinationClassifier:
    """
    Classifies if a generated text response is a hallucination.
    """
    def is_hallucinated(self, response: str, verified_facts: List[str]) -> bool:
        # If response contains claims not supported by any verified facts, flag as hallucination
        words = response.lower().replace(",", " ").replace(".", " ").split()

        has_verified_overlap = False
        for fact in verified_facts:
            fact_words = set(fact.lower().split())
            overlap = fact_words.intersection(words)
            if len(overlap) >= 2: # At least two overlapping contextual words
                has_verified_overlap = True

        return not has_verified_overlap


class EthicalGuardrails:
    """
    Intercepts and blocks requests violating SOSS safety guidelines.
    """
    def audit_query_safety(self, query: str) -> Dict[str, Any]:
        disallowed_keywords = ["cat /etc/passwd", "rm -rf", "drop table", "chmod 777", "exec Popen"]
        for kw in disallowed_keywords:
            if kw in query:
                return {
                    "safe": False,
                    "blocked_by": "EthicalGuardrails",
                    "reason": f"Disallowed system command keyword '{kw}' detected."
                }
        return {"safe": True, "blocked_by": None, "reason": "No policy violations detected."}


class TensorRefiner:
    """
    Aligns conceptual vectors to optimize coherence spatial density.
    """
    def align_tensor_clusters(self, clusters: List[List[float]]) -> List[List[float]]:
        # Compute mean center of the cluster vectors
        dim = len(clusters[0]) if clusters else 0
        if dim == 0:
            return clusters

        center = [0.0] * dim
        for v in clusters:
            for d in range(dim):
                center[d] += v[d]

        center = [x / len(clusters) for x in center]

        # Pull each vector slightly closer to the center to refine coherence
        refined = []
        for v in clusters:
            new_v = [round((v[d] * 0.90 + center[d] * 0.10), 4) for d in range(dim)]
            refined.append(new_v)
        return refined


class ConsensusBallotBox:
    """
    Executes strict multi-agent weighted votes.
    """
    def run_ballot(self, votes: Dict[str, float]) -> bool:
        # Ingests votes (weight values), returns True if sum > 2.5 (consensus threshold)
        return sum(votes.values()) >= 2.5
