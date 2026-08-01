import datetime
import uuid
import math
from typing import List, Dict, Any, Optional

from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.scoring.models import (
    MemoryFeatures,
    ScoringPolicy,
    DimensionScores,
    ScoreCard,
)

class MissingFeatureError(ValueError):
    pass

class CorruptedEvidenceError(ValueError):
    pass


def extract_features(record: KnowledgeCard, context: Optional[Dict[str, Any]] = None) -> MemoryFeatures:
    """
    Extracts raw numerical values for dimensions from a KnowledgeCard and its context.
    """
    context = context or {}

    # 1. Evidence Strength
    evidence = record.evidence
    evidence_strength = 0.0
    if evidence:
        # A simple proxy for evidence strength: longer, more structured evidence is slightly stronger,
        # but in a real system this might look for DOIs, links, data structures.
        evidence_strength = min(1.0, len(evidence.strip()) / 1000.0)
        # If it's explicitly "strong" in some external context
        if context.get("evidence_verified") is True:
            evidence_strength = max(evidence_strength, 0.8)

    # 2. Provenance Reliability
    provenance_reliability = 0.5 # Baseline
    if record.source_type == "USER":
        provenance_reliability = 0.9 # High trust for user input
    elif record.source_type == "SYSTEM":
        provenance_reliability = 0.7 # System generated
    elif record.source_type == "EXTERNAL":
        provenance_reliability = 0.6

    if context.get("provenance_verified") is True:
        provenance_reliability = 1.0

    # 3. Corroboration Level
    # Number of related cards / parent cards
    related_count = len(record.related_card_ids) + len(record.parent_card_ids)
    corroboration_level = min(1.0, related_count / 5.0)

    # 4. Specificity
    # Proxy: tags count + length of body (more specific tends to have more words)
    specificity = min(1.0, (len(record.tags) * 0.1) + (len(record.body) / 2000.0))

    # 5. Novelty
    # In context, how novel is this?
    novelty = context.get("novelty_score", 0.5)

    # 6. Utility
    # Based on "why_created", "problem_solved", "future_work_dependent"
    utility = 0.1
    if record.problem_solved:
        utility += 0.4
    if record.future_work_dependent:
        utility += 0.3
    if record.why_created:
        utility += 0.2

    # 7. Stability
    # Has it been superseded?
    stability = 1.0
    if record.superseded_by:
        stability = 0.0
    elif record.status == "DEPRECATED":
        stability = 0.0

    # 8. Contradiction Risk
    contradiction_risk = context.get("contradiction_risk", 0.0)
    if contradiction_risk < 0.0 or contradiction_risk > 1.0:
        raise CorruptedEvidenceError("Contradiction risk must be between 0 and 1.")

    # 9. Verification Status
    verification_status = 0.0
    if record.validation_state == "VALID":
        verification_status = 1.0
    elif record.validation_state == "UNVALIDATED":
        verification_status = 0.5
    elif record.validation_state == "INVALID":
        verification_status = 0.0

    # Calculate contextual/historical features
    now = datetime.datetime.now(datetime.timezone.utc)

    # Parse created_at safely
    try:
        created_at_str = record.created_at
        if created_at_str.endswith("Z"):
            created_at_str = created_at_str[:-1] + "+00:00"
        created_dt = datetime.datetime.fromisoformat(created_at_str)
        if created_dt.tzinfo is None:
            created_dt = created_dt.replace(tzinfo=datetime.timezone.utc)
        time_since_creation = max(0.0, (now - created_dt).total_seconds() / (24 * 3600))
    except Exception:
        time_since_creation = 0.0

    time_since_last_access = context.get("time_since_last_access", time_since_creation)
    access_count = context.get("access_count", 0)
    success_retrieval_count = context.get("success_retrieval_count", 0)
    failure_retrieval_count = context.get("failure_retrieval_count", 0)

    # Detect corrupted features (e.g., negative access count)
    if access_count < 0 or success_retrieval_count < 0 or failure_retrieval_count < 0:
         raise CorruptedEvidenceError("Counts cannot be negative.")

    return MemoryFeatures(
        evidence_strength=evidence_strength,
        provenance_reliability=provenance_reliability,
        corroboration_level=corroboration_level,
        specificity=specificity,
        novelty=novelty,
        utility=utility,
        stability=stability,
        contradiction_risk=contradiction_risk,
        verification_status=verification_status,
        time_since_creation=time_since_creation,
        time_since_last_access=time_since_last_access,
        access_count=access_count,
        success_retrieval_count=success_retrieval_count,
        failure_retrieval_count=failure_retrieval_count
    )


def apply_decay(score: float, features: MemoryFeatures, policy: ScoringPolicy, domain: str = "default") -> float:
    """Applies exponential decay based on the policy and time since last access."""
    if not policy.decay.enabled:
        return score

    half_life = policy.decay.half_life_days
    # Apply domain multiplier if exists
    if domain in policy.decay.domain_multipliers:
         half_life *= policy.decay.domain_multipliers[domain]

    if half_life <= 0:
        return score

    t = features.time_since_last_access
    # Exponential decay formula: N(t) = N0 * (1/2)^(t/t_half)
    decay_factor = math.pow(0.5, t / half_life)
    return score * decay_factor


def score(features: MemoryFeatures, policy: ScoringPolicy, card_id: str, domain: str = "default", _uuid_factory=uuid.uuid4, _clock=None) -> ScoreCard:
    if _clock is None:
        _clock = lambda: datetime.datetime.now(datetime.timezone.utc)
    """
    Calculates a weighted score using ScoringPolicy.
    Implements gates and fails closed on contradictions or bad verification.
    """
    # 1. Check Gates (Fail closed)
    if features.provenance_reliability < policy.gates.min_provenance:
        return _create_zero_score_card(features, policy, card_id, f"Failed provenance gate: {features.provenance_reliability} < {policy.gates.min_provenance}", _uuid_factory=_uuid_factory, _clock=_clock)

    if features.verification_status < policy.gates.min_verification:
        return _create_zero_score_card(features, policy, card_id, f"Failed verification gate: {features.verification_status} < {policy.gates.min_verification}", _uuid_factory=_uuid_factory, _clock=_clock)

    if features.contradiction_risk > policy.gates.max_contradiction:
        return _create_zero_score_card(features, policy, card_id, f"Failed contradiction gate: {features.contradiction_risk} > {policy.gates.max_contradiction}", _uuid_factory=_uuid_factory, _clock=_clock)

    # 2. Calculate Weighted Dimension Scores
    w = policy.weights

    dimensions = DimensionScores(
        evidence_strength=features.evidence_strength * w.evidence_strength,
        provenance_reliability=features.provenance_reliability * w.provenance_reliability,
        corroboration_level=features.corroboration_level * w.corroboration_level,
        specificity=features.specificity * w.specificity,
        novelty=features.novelty * w.novelty,
        utility=features.utility * w.utility,
        stability=features.stability * w.stability,
        contradiction_risk=0.0, # Contradiction is a penalty, handled below
        verification_status=0.0 # Used as a gate/multiplier, not an additive dimension
    )

    # 3. Sum weights and scores
    total_weight = (w.evidence_strength + w.provenance_reliability + w.corroboration_level +
                    w.specificity + w.novelty + w.utility + w.stability)

    if total_weight <= 0:
        total_weight = 1.0 # Prevent division by zero

    sum_scores = (dimensions.evidence_strength + dimensions.provenance_reliability +
                  dimensions.corroboration_level + dimensions.specificity +
                  dimensions.novelty + dimensions.utility + dimensions.stability)

    base_score = sum_scores / total_weight

    # 4. Apply Contradiction Penalty
    penalty = features.contradiction_risk * w.contradiction_penalty
    penalized_score = max(0.0, base_score - penalty)

    # 5. Apply Retrieval Outcomes Multiplier
    # If it's been retrieved often and failed often, reduce score
    total_retrievals = features.success_retrieval_count + features.failure_retrieval_count
    if total_retrievals > 0:
        success_rate = features.success_retrieval_count / total_retrievals
        # Smooth the success rate so new items aren't overly penalized
        smoothed_rate = (features.success_retrieval_count + 1) / (total_retrievals + 2)
        penalized_score *= smoothed_rate

    # Ensure bounded [0, 1]
    final_score = min(1.0, max(0.0, penalized_score))

    # 6. Apply Decay
    decayed_score = apply_decay(final_score, features, policy, domain)

    # 7. Generate Explanation
    explanation = (
        f"Base score {base_score:.3f} before penalties. "
        f"Contradiction penalty: -{penalty:.3f}. "
        f"Final decayed score: {decayed_score:.3f}. "
        f"Top contributors: "
    )
    # Find top contributing dimensions
    contribs = {k: getattr(dimensions, k) for k in DimensionScores.model_fields.keys() if k not in ('contradiction_risk', 'verification_status')}
    sorted_contribs = sorted(contribs.items(), key=lambda item: item[1], reverse=True)
    explanation += ", ".join([f"{k} (+{v/total_weight:.3f})" for k, v in sorted_contribs[:3]])

    card = ScoreCard(
        score_id=str(_uuid_factory()),
        card_id=card_id,
        policy_version=policy.version,
        final_score=final_score,
        dimensions=dimensions,
        raw_features=features,
        explanation=explanation,
        timestamp=_clock().isoformat(),
        decayed_score=decayed_score
    )
    _register_score(card)
    return card

def _create_zero_score_card(features: MemoryFeatures, policy: ScoringPolicy, card_id: str, reason: str, _uuid_factory=uuid.uuid4, _clock=None) -> ScoreCard:
    """Helper to return a zero score when a gate fails."""
    if _clock is None:
        _clock = lambda: datetime.datetime.now(datetime.timezone.utc)
    card = ScoreCard(
        score_id=str(_uuid_factory()),
        card_id=card_id,
        policy_version=policy.version,
        final_score=0.0,
        dimensions=DimensionScores(),
        raw_features=features,
        explanation=f"Score zeroed by gate: {reason}",
        timestamp=_clock().isoformat(),
        decayed_score=0.0
    )
    _register_score(card)
    return card


def rescore(records: List[KnowledgeCard], policy: ScoringPolicy, contexts: Optional[List[Dict[str, Any]]] = None) -> List[ScoreCard]:
    """Batch rescoring service."""
    if contexts is None:
        contexts = [{} for _ in records]

    if len(records) != len(contexts):
        raise ValueError("records and contexts must have the same length.")

    results = []
    for record, context in zip(records, contexts):
        features = extract_features(record, context)
        results.append(score(features, policy, record.card_id, domain=record.card_type))

    return results


def compare_scores(a: ScoreCard, b: ScoreCard) -> Dict[str, Any]:
    """Compares two ScoreCard objects and returns a dictionary of differences."""
    diff = {
        "final_score_diff": a.final_score - b.final_score,
        "decayed_score_diff": (a.decayed_score or 0.0) - (b.decayed_score or 0.0),
        "policy_diff": a.policy_version != b.policy_version,
        "dimension_diffs": {}
    }

    for field in DimensionScores.model_fields.keys():
        val_a = getattr(a.dimensions, field)
        val_b = getattr(b.dimensions, field)
        diff["dimension_diffs"][field] = val_a - val_b

    return diff



from collections import OrderedDict

class _LRUScoreRegistry:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: OrderedDict[str, ScoreCard] = OrderedDict()

    def add(self, score_card: ScoreCard) -> None:
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        self.cache[score_card.score_id] = score_card

    def get(self, score_id: str) -> Optional[ScoreCard]:
        if score_id in self.cache:
            self.cache.move_to_end(score_id)
            return self.cache[score_id]
        return None

_SCORE_REGISTRY = _LRUScoreRegistry(capacity=1000)

def _register_score(score_card: ScoreCard) -> None:
    """Internal registry to support explain(score_id) without a database."""
    _SCORE_REGISTRY.add(score_card)

def explain(score_id: str) -> str:
    """Returns the explanation string for a given score_id."""
    score_card = _SCORE_REGISTRY.get(score_id)
    if not score_card:
        return f"Score ID {score_id} not found in memory registry."
    return score_card.explanation
