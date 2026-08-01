import math
import uuid
from typing import List, Optional, Tuple, Any

from .models import (
    Claim, ContradictionEvidence, ContradictionCase,
    ResolutionPolicy, ResolutionProposal
)

def is_numeric(val: Any) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)

def get_temporal_overlap(claim_a: Claim, claim_b: Claim) -> bool:
    a_start = claim_a.scope.start_time or 0.0
    a_end = claim_a.scope.end_time or float('inf')
    b_start = claim_b.scope.start_time or 0.0
    b_end = claim_b.scope.end_time or float('inf')

    # Overlap if max(start) < min(end)
    return max(a_start, b_start) < min(a_end, b_end)

def check_numeric_conflict(val_a: Any, val_b: Any, tolerance: float) -> Tuple[bool, bool]:
    # Returns (is_conflict, is_numeric_comparison)
    if is_numeric(val_a) and is_numeric(val_b):
        diff = abs(val_a - val_b)
        denom = max(abs(val_a), abs(val_b), 1e-9)
        if (diff / denom) > tolerance:
            return True, True
        return False, True
    return False, False

def classify_contradiction(claim_a: Claim, claim_b: Claim, policy: ResolutionPolicy) -> Tuple[str, float]:
    """
    Classify the relationship between two claims and return (classification, severity).
    """
    if claim_a.entity != claim_b.entity or claim_a.predicate != claim_b.predicate:
        return "apparent/non-conflict", 0.0

    if claim_a.value == claim_b.value:
        # Same value, perhaps different sources or confidence
        # But this might not be a contradiction at all.
        return "apparent/non-conflict", 0.0

    # Values differ. Let's see why.

    # 1. Temporal
    if not get_temporal_overlap(claim_a, claim_b):
        return "temporal", 0.2

    # 2. Scoped
    if claim_a.scope.domain != claim_b.scope.domain and claim_a.scope.domain and claim_b.scope.domain:
        return "scoped", 0.3

    if set(claim_a.scope.tags) != set(claim_b.scope.tags) and (claim_a.scope.tags or claim_b.scope.tags):
        return "scoped", 0.4

    # 3. Numerical
    num_conflict, is_num = check_numeric_conflict(claim_a.value, claim_b.value, policy.numerical_tolerance)
    if is_num:
        if num_conflict:
            return "numerical", 0.6
        else:
            return "apparent/non-conflict", 0.0

    # 4. Definitional
    # If units differ in qualifiers, or string values are similar but not exact
    if isinstance(claim_a.value, str) and isinstance(claim_b.value, str):
        if claim_a.value.lower() == claim_b.value.lower():
            return "definitional", 0.5
        # Add basic unit check from qualifiers
        unit_a = claim_a.qualifiers.get("unit")
        unit_b = claim_b.qualifiers.get("unit")
        if unit_a and unit_b and unit_a != unit_b:
            return "definitional", 0.7

    # 5. Source Quality
    if claim_a.source_id != claim_b.source_id:
        conf_diff = abs(claim_a.scope.confidence - claim_b.scope.confidence)
        if conf_diff > 0.3:
            return "source-quality", 0.8

    # 6. Direct
    return "direct", 1.0


def propose_resolutions(classification: str, claim_a: Claim, claim_b: Claim, policy: ResolutionPolicy) -> List[ResolutionProposal]:
    proposals = []

    # helper for sorting claims by recency
    new_claim, old_claim = (claim_a, claim_b) if claim_a.timestamp >= claim_b.timestamp else (claim_b, claim_a)

    if classification == "apparent/non-conflict":
        proposals.append(ResolutionProposal(
            action="retain-both-with-scope",
            reason_code="NO_CONFLICT",
            explanation="Claims do not strictly contradict.",
            confidence=1.0,
            affected_claim_ids=[]
        ))
    elif classification == "temporal":
        proposals.append(ResolutionProposal(
            action="retain-both-with-scope",
            reason_code="TEMPORAL_SEPARATION",
            explanation="Claims apply to different time periods.",
            confidence=0.9,
            affected_claim_ids=[]
        ))
    elif classification == "scoped":
        proposals.append(ResolutionProposal(
            action="retain-both-with-scope",
            reason_code="SCOPE_DIFFERENCE",
            explanation="Claims apply to different domains or tags.",
            confidence=0.85,
            affected_claim_ids=[]
        ))
    elif classification == "numerical":
        proposals.append(ResolutionProposal(
            action="request-evidence",
            reason_code="NUMERICAL_DISCREPANCY",
            explanation="Values differ beyond permitted tolerance. Need more evidence to resolve.",
            confidence=0.7,
            affected_claim_ids=[claim_a.id, claim_b.id]
        ))
    elif classification == "definitional":
        proposals.append(ResolutionProposal(
            action="merge-definitions",
            reason_code="DEFINITIONAL_OVERLAP",
            explanation="Values represent the same underlying concept or differ in units.",
            confidence=0.75,
            affected_claim_ids=[claim_a.id, claim_b.id]
        ))
    elif classification == "source-quality":
        higher_conf_claim = claim_a if claim_a.scope.confidence > claim_b.scope.confidence else claim_b
        lower_conf_claim = claim_b if higher_conf_claim == claim_a else claim_a
        proposals.append(ResolutionProposal(
            action="lower-confidence",
            reason_code="SOURCE_QUALITY_MISMATCH",
            explanation=f"Lowering confidence of claim {lower_conf_claim.id} due to higher quality source for {higher_conf_claim.id}.",
            confidence=0.8,
            affected_claim_ids=[lower_conf_claim.id]
        ))
        proposals.append(ResolutionProposal(
            action="supersede",
            reason_code="SUPERSEDE_BY_QUALITY",
            explanation=f"Claim {higher_conf_claim.id} supersedes {lower_conf_claim.id}.",
            confidence=0.6,
            affected_claim_ids=[lower_conf_claim.id]
        ))
    elif classification == "direct":
        # Check recency
        if new_claim.timestamp > old_claim.timestamp:
            proposals.append(ResolutionProposal(
                action="supersede",
                reason_code="SUPERSEDE_BY_RECENCY",
                explanation=f"Newer claim {new_claim.id} supersedes older claim {old_claim.id}.",
                confidence=0.8,
                affected_claim_ids=[old_claim.id]
            ))
        else:
            proposals.append(ResolutionProposal(
                action="reject-new",
                reason_code="REJECT_NEW",
                explanation="Conflicting new claim without sufficient authority or recency.",
                confidence=0.5,
                affected_claim_ids=[new_claim.id]
            ))

    return proposals

def analyze_pair(claim_a: Claim, claim_b: Claim, policy: ResolutionPolicy) -> Optional[ContradictionCase]:
    classification, severity = classify_contradiction(claim_a, claim_b, policy)

    if classification == "apparent/non-conflict":
        return None

    proposals = propose_resolutions(classification, claim_a, claim_b, policy)

    # Priority is a mix of severity and policy weights
    priority_score = severity * 100.0

    # Generate deterministic ID
    ids = sorted([claim_a.id, claim_b.id])
    case_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"{ids[0]}_{ids[1]}"))

    return ContradictionCase(
        id=case_id,
        classification=classification,
        severity=severity,
        priority_score=priority_score,
        evidence=ContradictionEvidence(claim_a=claim_a, claim_b=claim_b),
        proposals=proposals,
        status="OPEN"
    )
