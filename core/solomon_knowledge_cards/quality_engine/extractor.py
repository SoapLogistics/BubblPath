import datetime
from typing import Dict, Any
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.quality_engine.models import MemoryFeatures

def extract_features(card: KnowledgeCard, context: Dict[str, Any] = None) -> MemoryFeatures:
    """
    Extracts numerical features for the quality engine from a KnowledgeCard and optional external context.
    Fails closed/returns 0 for corrupted or missing evidence safely.
    """
    context = context or {}

    # Evidence
    evidence_strength = 0.0
    if card.evidence and isinstance(card.evidence, str):
        evidence_strength = 0.5
        if len(card.evidence) > 100:
            evidence_strength = 0.8

    # Provenance
    provenance_reliability = 0.0 # FAIL CLOSED: Missing provenance is a failure
    if card.source_ids:
        provenance_reliability = 0.8

    # Corroboration
    corroboration_count = 0
    if card.related_card_ids:
        corroboration_count += len(card.related_card_ids)
    if card.parent_card_ids:
        corroboration_count += len(card.parent_card_ids)

    # Specificity
    specificity_score = 0.0 # FAIL CLOSED: Missing specificity is a failure
    if card.body and isinstance(card.body, str) and len(card.body) > 200:
        specificity_score = min(1.0, len(card.body) / 1000.0)

    # Freshness
    freshness_days = 9999.0 # FAIL CLOSED: Corrupt dates are treated as infinitely old
    if card.created_at:
        try:
            created_at = datetime.datetime.fromisoformat(card.created_at.replace("Z", "+00:00"))
            now = datetime.datetime.now(datetime.timezone.utc)
            freshness_days = max(0.0, float((now - created_at).days))
        except ValueError:
            pass # fallback to 9999.0

    # Utility
    retrieval_count = 0
    if card.extra_metadata:
        retrieval_count = card.extra_metadata.get("retrieval_count", 0)

    # Contradiction
    contradiction_risk = context.get("contradiction_risk", 0.0)

    # Verification
    verification_status = 1.0 if card.validation_state == "VALID" else (0.0 if card.validation_state == "INVALID" else 0.5)

    # Stability
    stability_score = 1.0 if card.status in ("APPROVED", "ACTIVE") else 0.5

    # Domain
    domain = "default"
    if card.tags and "fast-decay" in card.tags:
        domain = "fast_decay"

    return MemoryFeatures(
        evidence_strength=evidence_strength,
        provenance_reliability=provenance_reliability,
        corroboration_count=corroboration_count,
        specificity_score=specificity_score,
        freshness_days=freshness_days,
        novelty_score=context.get("novelty_score", 0.5),
        utility_retrieval_count=retrieval_count,
        stability_score=stability_score,
        contradiction_risk=contradiction_risk,
        verification_status=verification_status,
        domain=domain
    )
