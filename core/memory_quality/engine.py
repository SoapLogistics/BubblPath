import uuid
import datetime
import math
from typing import Dict, Any, List, Optional
from core.memory_quality.models import QualityDimensions, ScoringPolicy, ScoreExplanation, MemoryQualityScore

def extract_features(record: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> QualityDimensions:
    """
    Extracts QualityDimensions features from a memory record (e.g., KnowledgeCard dictionary representation)
    and optional contextual data.
    """
    if context is None:
        context = {}

    # Extract dimensions using naive heuristics based on expected fields,
    # mapping real-world record metadata to a 0.0-1.0 float scale.

    # Evidence: Length or specific indicators of evidence
    evidence_text = record.get("evidence", "")
    evidence_strength = min(1.0, len(evidence_text) / 500.0) if evidence_text else 0.0

    # Provenance: Reliability of the source
    source_type = record.get("source_type", "")
    provenance_mapping = {
        "verified_human": 1.0,
        "official_system": 0.9,
        "sensor": 0.8,
        "inferred": 0.5,
        "untrusted": 0.1
    }
    provenance = provenance_mapping.get(source_type.lower(), 0.3)

    # Corroboration: based on related_card_ids count or external corroborations in context
    related_ids = record.get("related_card_ids", [])
    corroboration = min(1.0, len(related_ids) / 5.0)

    # Specificity: Length of body + summary, or tags count
    body = record.get("body", "")
    specificity = min(1.0, (len(body) / 1000.0) + (len(record.get("tags", [])) * 0.05))

    # Freshness: Based on created_at or updated_at
    updated_at_str = record.get("updated_at")
    freshness = 1.0
    if updated_at_str:
        try:
            val_to_parse = updated_at_str
            if val_to_parse.endswith("Z"):
                val_to_parse = val_to_parse[:-1] + "+00:00"
            updated_at = datetime.datetime.fromisoformat(val_to_parse)
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=datetime.UTC)

            now = datetime.datetime.now(datetime.UTC)
            days_old = (now - updated_at).days
            # Simple freshness curve
            freshness = max(0.0, 1.0 - (days_old / 365.0))
        except Exception:
            pass

    # Novelty: Inverse of related/parent cards or explicit context
    novelty = 1.0 - min(1.0, len(record.get("parent_card_ids", [])) / 3.0)

    # Utility: Can be based on access count or access history if provided in context
    access_count = context.get("access_count", 0)
    utility = min(1.0, access_count / 100.0)

    # Stability: Inverse of volatility or updates
    update_count = context.get("update_count", 0)
    stability = max(0.0, 1.0 - (update_count / 20.0))

    # Contradiction Risk: Based on context or explicit flags
    contradiction_risk = context.get("contradiction_risk", 0.0)

    # Verification Status
    verification_status = record.get("validation_state", "UNVALIDATED")

    return QualityDimensions(
        evidence=evidence_strength,
        provenance=provenance,
        corroboration=corroboration,
        specificity=specificity,
        freshness=freshness,
        novelty=novelty,
        utility=utility,
        stability=stability,
        contradiction_risk=contradiction_risk,
        verification_status=verification_status
    )

def score(features: QualityDimensions, policy: ScoringPolicy, domain: Optional[str] = None) -> ScoreExplanation:
    """
    Calculates the quality score given a set of features and a scoring policy.
    Applies strict gating and domain-aware decay logic.
    """
    # Initialize variables
    gated = False
    gate_reason = None
    dimension_contributions = {}
    base_score = 0.0

    # Check gates
    if "min_provenance" in policy.gates and features.provenance < policy.gates["min_provenance"]:
        gated = True
        gate_reason = f"Provenance ({features.provenance}) below minimum ({policy.gates['min_provenance']})"
    elif "required_verification" in policy.gates and features.verification_status not in policy.gates["required_verification"]:
        gated = True
        gate_reason = f"Verification status '{features.verification_status}' not in required list {policy.gates['required_verification']}"
    elif "max_contradiction_risk" in policy.gates and features.contradiction_risk > policy.gates["max_contradiction_risk"]:
        gated = True
        gate_reason = f"Contradiction risk ({features.contradiction_risk}) above maximum ({policy.gates['max_contradiction_risk']})"

    # Calculate weighted average
    total_weight = sum(policy.weights.values())

    if total_weight > 0:
        for dim, weight in policy.weights.items():
            val = getattr(features, dim, 0.0)
            if dim == 'contradiction_risk':
                # For contradiction_risk, higher is worse, so we invert it for scoring.
                contribution = (1.0 - val) * weight
            else:
                contribution = val * weight

            dimension_contributions[dim] = contribution
            base_score += contribution

        base_score /= total_weight

    # Apply decay
    decay_rate = policy.default_decay_rate
    if domain and domain in policy.domain_decay_rates:
        decay_rate = policy.domain_decay_rates[domain]

    # Decay penalty is a function of (1 - freshness) and decay_rate.
    decay_penalty = (1.0 - features.freshness) * decay_rate * 0.5 # 0.5 is scaling factor

    final_score = base_score - decay_penalty

    if gated:
        final_score = 0.0 # Force to 0 if gated

    return ScoreExplanation(
        base_score=max(0.0, min(1.0, base_score)),
        gated=gated,
        gate_reason=gate_reason,
        dimension_contributions=dimension_contributions,
        decay_penalty=max(0.0, decay_penalty)
    )

def rescore(records: List[Dict[str, Any]], policy: ScoringPolicy, repository, contexts: Optional[List[Dict[str, Any]]] = None, domains: Optional[List[str]] = None) -> List[MemoryQualityScore]:
    """
    Batch rescores a list of records using the provided policy.
    Scores are saved to the repository and returned.
    """
    scores = []

    if contexts is None:
        contexts = [{} for _ in records]

    if domains is None:
        domains = [None for _ in records]

    for i, record in enumerate(records):
        context = contexts[i] if i < len(contexts) else {}
        domain = domains[i] if i < len(domains) else None

        features = extract_features(record, context)
        explanation = score(features, policy, domain)

        # Determine record ID based on common conventions
        record_id = record.get("card_id") or record.get("id") or str(uuid.uuid4())

        final_score = max(0.0, min(1.0, explanation.base_score - explanation.decay_penalty))
        if explanation.gated:
            final_score = 0.0

        memory_score = MemoryQualityScore(
            record_id=record_id,
            policy_version=policy.version,
            final_score=final_score,
            features_snapshot=features,
            explanation=explanation
        )

        if repository:
            repository.save_score(memory_score)

        scores.append(memory_score)

    return scores

def compare_scores(score_a: MemoryQualityScore, score_b: MemoryQualityScore) -> Dict[str, Any]:
    """
    Compares two scores and returns a summary of the differences.
    """
    return {
        "final_score_diff": score_b.final_score - score_a.final_score,
        "policy_version_change": score_a.policy_version != score_b.policy_version,
        "gated_change": score_a.explanation.gated != score_b.explanation.gated,
        "dimension_diffs": {
            dim: getattr(score_b.features_snapshot, dim) - getattr(score_a.features_snapshot, dim)
                for dim in type(score_a.features_snapshot).model_fields.keys()
                if isinstance(getattr(score_a.features_snapshot, dim), (int, float))
        }
    }

def explain(score_id: str, repository) -> Optional[Dict[str, Any]]:
    """
    Retrieves a score by ID from the repository and provides a full explanation summary.
    """
    score_obj = repository.get_score(score_id)
    if not score_obj:
        return None

    return {
        "score_id": score_obj.score_id,
        "record_id": score_obj.record_id,
        "policy_version": score_obj.policy_version,
        "timestamp": score_obj.timestamp.isoformat(),
        "final_score": score_obj.final_score,
        "gated": score_obj.explanation.gated,
        "gate_reason": score_obj.explanation.gate_reason,
        "base_score": score_obj.explanation.base_score,
        "decay_penalty": score_obj.explanation.decay_penalty,
        "dimension_contributions": score_obj.explanation.dimension_contributions,
        "feature_snapshot": score_obj.features_snapshot.model_dump()
    }
