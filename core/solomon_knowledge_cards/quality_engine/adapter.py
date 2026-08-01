from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.quality_engine.models import QualityScore

def apply_score_to_card(card: KnowledgeCard, quality_score: QualityScore) -> KnowledgeCard:
    """
    Updates a KnowledgeCard's confidence field using the new QualityScore.
    Stores the full QualityScore in an append-only history in extra_metadata for auditability.
    """
    card.confidence = quality_score.final_score

    if not card.extra_metadata:
        card.extra_metadata = {}

    if "quality_score_history" not in card.extra_metadata:
        card.extra_metadata["quality_score_history"] = []

    card.extra_metadata["quality_score_history"].append(quality_score.model_dump())

    # Optional shortcut to latest score
    card.extra_metadata["latest_quality_score"] = quality_score.model_dump()

    return card
