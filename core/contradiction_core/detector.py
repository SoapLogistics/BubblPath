import uuid
import re
from typing import List, Tuple, Optional, Dict
from .models import (
    Claim, ContradictionEvidence, ContradictionCase, ResolutionPolicy,
    ResolutionProposal
)

def extract_number(value_str: str) -> Optional[float]:
    match = re.search(r'[-+]?\d*\.\d+|\d+', value_str)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None

def detect(claims_and_evidence: List[Tuple[Claim, ContradictionEvidence]], policy: ResolutionPolicy) -> List[ContradictionCase]:
    cases = []
    seen_pairs = set()

    for i, (claim1, ev1) in enumerate(claims_and_evidence):
        for j in range(i + 1, len(claims_and_evidence)):
            claim2, ev2 = claims_and_evidence[j]

            # Only compare claims about the same entity and predicate
            if claim1.entity == claim2.entity and claim1.predicate == claim2.predicate:
                # If they have the exact same fingerprint, they are identical, not a contradiction
                if claim1.fingerprint() == claim2.fingerprint():
                    continue

                fp_pair = tuple(sorted([claim1.fingerprint(), claim2.fingerprint()]))
                if fp_pair in seen_pairs:
                    continue
                seen_pairs.add(fp_pair)

                classification = classify(claim1, claim2, policy, ev1, ev2)

                # We only consider it a case if it's a conflict or apparent conflict
                if classification:
                    case_id = str(uuid.uuid4())

                    case = ContradictionCase(
                        case_id=case_id,
                        claim1=claim1,
                        claim2=claim2,
                        evidence1=ev1,
                        evidence2=ev2,
                        classification=classification
                    )

                    case.severity = _calculate_severity(case)
                    case.uncertainty = _calculate_uncertainty(case)
                    case.proposals = propose_resolution(case, policy)

                    cases.append(case)

    return cases

def classify(claim1: Claim, claim2: Claim, policy: ResolutionPolicy, evidence1: Optional[ContradictionEvidence] = None, evidence2: Optional[ContradictionEvidence] = None) -> Optional[str]:
    # Check if temporal scopes are disjoint
    if policy.temporal_strictness and claim1.scope.is_disjoint_temporal(claim2.scope):
        return "TEMPORAL"

    # Check if other scopes are disjoint
    if claim1.scope.is_disjoint_geospatial(claim2.scope) or claim1.scope.is_disjoint_context(claim2.scope):
        return "SCOPED"

    # Check for Definitional conflict (e.g., same term, different fundamental definition)
    # Here we infer a definitional conflict if the predicate is "definition" or "is_a" and the objects differ.
    if claim1.predicate in ["definition", "is_a", "meaning"] and claim1.object_value != claim2.object_value:
        return "DEFINITIONAL"

    # Check for Source Quality conflict
    # If the claims are directly conflicting but one source is known to be terrible and the other excellent,
    # it's a conflict rooted in source quality rather than a true anomaly.
    if evidence1 and evidence2:
        qual_diff = abs(evidence1.source_quality - evidence2.source_quality)
        if qual_diff > policy.source_quality_threshold and claim1.object_value != claim2.object_value:
            return "SOURCE_QUALITY"

    # Numerical Check
    num1 = extract_number(claim1.object_value)
    num2 = extract_number(claim2.object_value)

    if num1 is not None and num2 is not None:
        if claim1.unit == claim2.unit:
            diff = abs(num1 - num2)
            avg = (abs(num1) + abs(num2)) / 2.0

            if avg > 0:
                rel_diff = diff / avg
                if rel_diff <= policy.numerical_tolerance:
                    return "APPARENT_NON_CONFLICT"
                else:
                    return "NUMERICAL"
            elif diff == 0:
                return "APPARENT_NON_CONFLICT"
            else:
                return "NUMERICAL"

    # If it's not a numeric conflict, and scopes overlap, and objects differ
    if claim1.object_value != claim2.object_value:
        return "DIRECT"

    return "APPARENT_NON_CONFLICT"

def _calculate_severity(case: ContradictionCase) -> float:
    if case.classification == "APPARENT_NON_CONFLICT":
        return 0.0
    if case.classification in ["TEMPORAL", "SCOPED"]:
        return 0.2

    # Direct conflicts are more severe if both have high confidence
    confidence_factor = (case.evidence1.confidence * case.evidence2.confidence)
    quality_factor = (case.evidence1.source_quality * case.evidence2.source_quality)

    base = 0.5
    if case.classification == "DIRECT":
        base = 0.8
    elif case.classification == "NUMERICAL":
        base = 0.6

    return min(1.0, base + (confidence_factor * 0.1) + (quality_factor * 0.1))

def _calculate_uncertainty(case: ContradictionCase) -> float:
    # High uncertainty if evidence is weak or qualities are drastically different
    qual_diff = abs(case.evidence1.source_quality - case.evidence2.source_quality)
    conf_diff = abs(case.evidence1.confidence - case.evidence2.confidence)

    avg_conf = (case.evidence1.confidence + case.evidence2.confidence) / 2

    return min(1.0, qual_diff * 0.3 + conf_diff * 0.3 + (1 - avg_conf) * 0.4)

def rank(cases: List[ContradictionCase]) -> List[ContradictionCase]:
    # Rank by severity descending, then uncertainty ascending
    return sorted(cases, key=lambda c: (-c.severity, c.uncertainty))

def propose_resolution(case: ContradictionCase, policy: ResolutionPolicy) -> List[ResolutionProposal]:
    proposals = []

    if case.classification in ["TEMPORAL", "SCOPED"]:
        proposals.append(ResolutionProposal(
            action="RETAIN_BOTH_WITH_SCOPE",
            reason_code="NON_OVERLAPPING_SCOPE",
            details={"message": f"Claims have disjoint {case.classification.lower()} scopes and can co-exist."}
        ))

    elif case.classification == "APPARENT_NON_CONFLICT":
        proposals.append(ResolutionProposal(
            action="RETAIN_BOTH_WITH_SCOPE",
            reason_code="WITHIN_TOLERANCE",
            details={"message": "Claims are considered functionally equivalent."}
        ))

    elif case.classification in ["DIRECT", "NUMERICAL"]:
        # If one source is significantly better than another
        diff_qual = case.evidence1.source_quality - case.evidence2.source_quality
        diff_conf = case.evidence1.confidence - case.evidence2.confidence

        if diff_qual > 0.3 or (diff_qual > 0 and diff_conf > 0.2):
            proposals.append(ResolutionProposal(
                action="SUPERSEDE",
                reason_code="HIGHER_QUALITY_SOURCE",
                details={
                    "superseding_claim_id": case.claim1.claim_id,
                    "superseded_claim_id": case.claim2.claim_id
                }
            ))
        elif diff_qual < -0.3 or (diff_qual < 0 and diff_conf < -0.2):
            proposals.append(ResolutionProposal(
                action="SUPERSEDE",
                reason_code="HIGHER_QUALITY_SOURCE",
                details={
                    "superseding_claim_id": case.claim2.claim_id,
                    "superseded_claim_id": case.claim1.claim_id
                }
            ))
        else:
            proposals.append(ResolutionProposal(
                action="REQUEST_EVIDENCE",
                reason_code="AMBIGUOUS_CONFLICT",
                details={"message": "Sources have similar quality and confidence; manual review or more evidence needed."}
            ))
            proposals.append(ResolutionProposal(
                action="LOWER_CONFIDENCE",
                reason_code="CONFLICTING_CLAIMS_DETECTED",
                details={"penalty": 0.2}
            ))

    return proposals

def explain(case: ContradictionCase) -> str:
    explanation = [
        f"Contradiction Case: {case.case_id}",
        f"Classification: {case.classification}",
        f"Severity: {case.severity:.2f}, Uncertainty: {case.uncertainty:.2f}",
        "",
        "Claim 1:",
        f"  - Entity: {case.claim1.entity}",
        f"  - Predicate: {case.claim1.predicate}",
        f"  - Value: {case.claim1.object_value} {case.claim1.unit or ''}",
        f"  - Confidence: {case.evidence1.confidence:.2f}",
        f"  - Source Quality: {case.evidence1.source_quality:.2f}",
        "",
        "Claim 2:",
        f"  - Entity: {case.claim2.entity}",
        f"  - Predicate: {case.claim2.predicate}",
        f"  - Value: {case.claim2.object_value} {case.claim2.unit or ''}",
        f"  - Confidence: {case.evidence2.confidence:.2f}",
        f"  - Source Quality: {case.evidence2.source_quality:.2f}",
        "",
        "Proposed Resolutions:"
    ]

    for i, prop in enumerate(case.proposals):
        explanation.append(f"  {i+1}. {prop.action} ({prop.reason_code}) - {prop.details}")

    return "\n".join(explanation)
