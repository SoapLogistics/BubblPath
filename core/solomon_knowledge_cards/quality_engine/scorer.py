import datetime
import uuid
import math
from typing import Dict, Any
from core.solomon_knowledge_cards.quality_engine.models import MemoryFeatures, ScoringPolicy, QualityScore

def compute_decay(features: MemoryFeatures, policy: ScoringPolicy) -> float:
    """Computes freshness score after domain-aware exponential decay. Returns [0.0, 1.0]."""
    half_life = policy.decay_params.get("default_half_life_days", 365.0)
    if features.domain == "fast_decay":
        half_life = policy.decay_params.get("fast_decay_half_life_days", 30.0)

    # N(t) = N0 * (1/2) ^ (t / t_half)
    decay_factor = math.pow(0.5, features.freshness_days / half_life)
    return decay_factor

def score(features: MemoryFeatures, policy: ScoringPolicy, card_id: str) -> QualityScore:
    """Applies weights, gates, and decay to produce a final QualityScore."""
    components = {}
    reason_codes = []

    components["evidence"] = features.evidence_strength
    components["provenance"] = features.provenance_reliability

    # Normalize corroboration (cap at 5 for max score)
    corrob_norm = min(1.0, features.corroboration_count / 5.0)
    components["corroboration"] = corrob_norm

    components["specificity"] = features.specificity_score
    components["novelty"] = features.novelty_score

    # Normalize utility (cap at 10 for max score)
    utility_norm = min(1.0, features.utility_retrieval_count / 10.0)
    components["utility"] = utility_norm

    components["stability"] = features.stability_score
    components["contradiction_risk"] = features.contradiction_risk
    components["verification_status"] = features.verification_status

    decayed_freshness = compute_decay(features, policy)
    components["freshness"] = decayed_freshness

    base_score = 0.0
    for dim, weight in policy.weights.items():
        val = components.get(dim, 0.0)
        base_score += val * weight

    # Gates
    gated_by = None
    max_score = 1.0
    for gate_dim, threshold in policy.gates.items():
        if components.get(gate_dim, 0.0) < threshold:
            max_score = min(max_score, 0.4) # cap score heavily if gate fails
            gated_by = gate_dim
            reason_codes.append(f"GATED_BY_{gate_dim.upper()}")

    final_score = min(base_score, max_score)
    final_score = max(0.0, final_score) # Bound to [0.0, 1.0]

    if final_score < 0.3:
        reason_codes.append("LOW_CONFIDENCE")
    elif final_score > 0.8:
        reason_codes.append("HIGH_CONFIDENCE")

    if components.get("contradiction_risk", 0.0) > 0.5:
        reason_codes.append("HIGH_CONTRADICTION_RISK")

    return QualityScore(
        score_id=str(uuid.uuid4()),
        card_id=card_id,
        policy_version=policy.version,
        final_score=final_score,
        components=components,
        gated_by=gated_by,
        reason_codes=reason_codes,
        computed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        feature_snapshot=features
    )

def explain(score_obj: QualityScore) -> str:
    """Generates a human-readable explanation of the score."""
    lines = [f"Quality Score Explanation for Card {score_obj.card_id} (Policy v{score_obj.policy_version})"]
    lines.append(f"Final Score: {score_obj.final_score:.2f}")
    if score_obj.gated_by:
        lines.append(f"WARNING: Score was capped by failed gate on dimension: {score_obj.gated_by}")

    lines.append("Component Breakdown:")
    for dim, val in score_obj.components.items():
        lines.append(f"  - {dim}: {val:.2f}")

    if score_obj.reason_codes:
        lines.append("Reason Codes: " + ", ".join(score_obj.reason_codes))

    return "\n".join(lines)

def compare_scores(a: QualityScore, b: QualityScore) -> Dict[str, Any]:
    """Compares two scores and returns delta analysis."""
    return {
        "score_delta": a.final_score - b.final_score,
        "policy_transition": f"{b.policy_version} -> {a.policy_version}",
        "reason_code_changes": {
            "added": list(set(a.reason_codes) - set(b.reason_codes)),
            "removed": list(set(b.reason_codes) - set(a.reason_codes))
        }
    }
