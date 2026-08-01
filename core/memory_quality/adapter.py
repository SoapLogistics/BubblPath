from typing import Dict, Any, List
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.memory_quality.models import ScoringPolicy, MemoryQualityScore
from core.memory_quality.engine import extract_features, score

def adapt_card_confidence(card: KnowledgeCard, policy: ScoringPolicy, repository, context: Dict[str, Any] = None) -> KnowledgeCard:
    """
    Adapts an existing KnowledgeCard to use the v2 engine for its confidence score.
    Returns a modified KnowledgeCard without data loss.
    """
    # 1. Convert card to dict for feature extraction
    card_dict = card.to_dict()

    # 2. Add existing confidence to context for potential heuristic use
    if context is None:
        context = {}
    context["legacy_confidence"] = card.confidence

    # 3. Extract features and compute new score
    features = extract_features(card_dict, context)

    # Optional domain extraction from tags
    domain = next((tag.split(":")[1] for tag in card.tags if tag.startswith("domain:")), None)

    explanation = score(features, policy, domain)

    final_score = max(0.0, min(1.0, explanation.base_score - explanation.decay_penalty))
    if explanation.gated:
        final_score = 0.0

    # 4. Save to repository
    memory_score = MemoryQualityScore(
        record_id=card.card_id,
        policy_version=policy.version,
        final_score=final_score,
        features_snapshot=features,
        explanation=explanation
    )

    if repository:
        repository.save_score(memory_score)

    # 5. Update the card's confidence field natively
    # We update both the confidence and possibly validation state
    card.confidence = final_score

    # If the engine completely gated it based on verification or provenance,
    # we might consider adjusting validation state, but to prevent data loss
    # and strictly comply with rules, we only mutate confidence and store the detailed
    # v2 score info in extra_metadata.

    if card.extra_metadata is None:
        card.extra_metadata = {}

    card.extra_metadata["v2_score_id"] = memory_score.score_id
    card.extra_metadata["v2_policy_version"] = memory_score.policy_version
    card.extra_metadata["v2_final_score"] = memory_score.final_score

    # Must re-validate to ensure model integrity
    card.validate()

    return card

def batch_adapt_cards(cards: List[KnowledgeCard], policy: ScoringPolicy, repository, contexts: List[Dict[str, Any]] = None) -> List[KnowledgeCard]:
    """
    Adapts a batch of KnowledgeCards using the v2 engine.
    """
    if contexts is None:
        contexts = [{} for _ in cards]

    adapted = []
    for i, card in enumerate(cards):
        ctx = contexts[i] if i < len(contexts) else {}
        adapted.append(adapt_card_confidence(card, policy, repository, ctx))

    return adapted
