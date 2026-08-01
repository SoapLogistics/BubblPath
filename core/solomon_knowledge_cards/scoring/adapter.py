from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.scoring.models import ScoreCard

def update_confidence_from_score(record: KnowledgeCard, score_card: ScoreCard, use_decayed: bool = True) -> KnowledgeCard:
    """
    Updates the confidence field of a KnowledgeCard using the result of a ScoreCard.
    Does not modify the original record, returns a modified copy.
    """
    record_dict = record.to_dict()

    if use_decayed and score_card.decayed_score is not None:
        new_confidence = score_card.decayed_score
    else:
        new_confidence = score_card.final_score

    record_dict["confidence"] = new_confidence

    # Store score_id and policy_version in extra_metadata for auditability
    if "extra_metadata" not in record_dict or record_dict["extra_metadata"] is None:
        record_dict["extra_metadata"] = {}

    record_dict["extra_metadata"]["last_score_id"] = score_card.score_id
    record_dict["extra_metadata"]["last_score_policy"] = score_card.policy_version
    record_dict["extra_metadata"]["last_score_timestamp"] = score_card.timestamp

    return KnowledgeCard.from_dict(record_dict)
