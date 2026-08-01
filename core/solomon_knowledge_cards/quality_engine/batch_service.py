from typing import List, Dict, Any
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.quality_engine.models import ScoringPolicy, QualityScore
from core.solomon_knowledge_cards.quality_engine.extractor import extract_features
from core.solomon_knowledge_cards.quality_engine.scorer import score

def rescore(records: List[KnowledgeCard], policy: ScoringPolicy, contexts: Dict[str, Dict[str, Any]] = None) -> Dict[str, QualityScore]:
    """
    Batch rescores a list of knowledge cards.
    contexts is an optional dictionary mapping card_id to a context dictionary.
    """
    contexts = contexts or {}
    results = {}

    for card in records:
        context = contexts.get(card.card_id, {})
        features = extract_features(card, context)
        q_score = score(features, policy, card.card_id)
        results[card.card_id] = q_score

    return results
