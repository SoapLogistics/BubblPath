import pytest
import json
import os
import datetime

from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.scoring.models import ScoringPolicy, DecayPolicy, ScoringGates
from core.solomon_knowledge_cards.scoring.engine import (
    extract_features,
    score,
    rescore,
    compare_scores,
    apply_decay,
    MissingFeatureError,
    CorruptedEvidenceError
)
from core.solomon_knowledge_cards.scoring.adapter import update_confidence_from_score


@pytest.fixture
def base_policy():
    return ScoringPolicy(
        version="1.0.0",
        decay=DecayPolicy(enabled=False)
    )


@pytest.fixture
def valid_record_dict():
    return {
        "card_id": "test-123",
        "card_type": "KNOWLEDGE",
        "schema_version": "1.0",
        "title": "Test Title",
        "summary": "Test Summary",
        "body": "Test Body",
        "status": "ACTIVE",
        "confidence": 0.5,
        "validation_state": "UNVALIDATED",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "tester",
        "source_type": "USER",
        "source_ids": [],
        "parent_card_ids": [],
        "related_card_ids": [],
        "tags": ["test"],
        "security_classification": "UNCLASSIFIED",
        "evidence": "Some evidence here.",
        "why_created": "",
        "problem_solved": "",
        "future_work_dependent": ""
    }


def test_extract_features(valid_record_dict):
    record = KnowledgeCard.from_dict(valid_record_dict)
    context = {"access_count": 10, "novelty_score": 0.8}
    features = extract_features(record, context)

    assert features.access_count == 10
    assert features.novelty == 0.8
    assert features.provenance_reliability == 0.9 # USER source
    assert features.verification_status == 0.5 # UNVALIDATED


def test_corrupted_features(valid_record_dict):
    record = KnowledgeCard.from_dict(valid_record_dict)
    context = {"access_count": -5} # Corrupted
    with pytest.raises(CorruptedEvidenceError):
        extract_features(record, context)


def test_scoring_gates(valid_record_dict, base_policy):
    record = KnowledgeCard.from_dict(valid_record_dict)
    features = extract_features(record)

    # Policy requires verified
    gated_policy = base_policy.model_copy(deep=True)
    gated_policy.gates.min_verification = 1.0

    score_card = score(features, gated_policy, record.card_id)
    assert score_card.final_score == 0.0
    assert "Failed verification gate" in score_card.explanation


def test_contradiction_penalty(valid_record_dict, base_policy):
    record = KnowledgeCard.from_dict(valid_record_dict)

    # Score without contradiction
    f1 = extract_features(record, {"contradiction_risk": 0.0})
    s1 = score(f1, base_policy, record.card_id)

    # Score with contradiction
    f2 = extract_features(record, {"contradiction_risk": 0.5})
    s2 = score(f2, base_policy, record.card_id)

    assert s2.final_score < s1.final_score


def test_decay(valid_record_dict):
    record = KnowledgeCard.from_dict(valid_record_dict)

    policy = ScoringPolicy(
        version="1.0.0",
        decay=DecayPolicy(enabled=True, half_life_days=30.0)
    )

    # Access just now
    f1 = extract_features(record, {"time_since_last_access": 0.0})
    s1 = score(f1, policy, record.card_id)
    assert s1.decayed_score == s1.final_score

    # Access 30 days ago (half-life)
    f2 = extract_features(record, {"time_since_last_access": 30.0})
    s2 = score(f2, policy, record.card_id)
    assert s2.decayed_score == pytest.approx(s2.final_score * 0.5)


def test_adapter(valid_record_dict, base_policy):
    record = KnowledgeCard.from_dict(valid_record_dict)
    features = extract_features(record)
    score_card = score(features, base_policy, record.card_id)

    updated_record = update_confidence_from_score(record, score_card)
    assert updated_record.confidence == score_card.final_score
    assert updated_record.extra_metadata["last_score_id"] == score_card.score_id
    # Ensure immutability of original
    assert record.confidence == 0.5


def test_batch_rescore(valid_record_dict, base_policy):
    r1 = KnowledgeCard.from_dict(valid_record_dict)

    dict2 = valid_record_dict.copy()
    dict2["card_id"] = "test-456"
    dict2["validation_state"] = "VALID"
    r2 = KnowledgeCard.from_dict(dict2)

    records = [r1, r2]
    contexts = [{}, {"evidence_verified": True}]

    results = rescore(records, base_policy, contexts)

    assert len(results) == 2
    assert results[0].card_id == "test-123"
    assert results[1].card_id == "test-456"
    assert results[1].final_score > results[0].final_score


def test_calibration_fixtures():
    fixtures_path = os.path.join(os.path.dirname(__file__), "fixtures", "scoring", "calibration_fixtures.json")
    with open(fixtures_path, "r") as f:
        fixtures = json.load(f)

    policy = ScoringPolicy(version="1.0.0", decay=DecayPolicy(enabled=False))

    scores = []
    for fx in fixtures:
        record = KnowledgeCard.from_dict(fx["record"])
        features = extract_features(record, fx["context"])

        # Override gates for the frequently retrieved wrong fixture test, to ensure it doesn't just hit 0
        test_policy = policy.model_copy(deep=True)
        if fx["fixture_id"] == "F3_FREQUENTLY_RETRIEVED_WRONG":
             test_policy.gates.max_contradiction = 1.0 # Allow it through to see the score impact

        score_card = score(features, test_policy, record.card_id)

        min_expected, max_expected = fx["expected_score_range"]

        # Validate expected score range
        assert min_expected <= score_card.final_score <= max_expected, f"Score {score_card.final_score} out of bounds [{min_expected}, {max_expected}] for {fx['fixture_id']}"


        scores.append((fx["fixture_id"], score_card.final_score, fx["expected_rank"]))

    # Sort by actual score
    scores.sort(key=lambda x: x[1], reverse=True)

    # Extract actual ranks based on sorted scores
    actual_ranks = {item[0]: idx + 1 for idx, item in enumerate(scores)}

    # Assert ranks match expected
    for fx_id, _, expected_rank in scores:
        assert actual_ranks[fx_id] == expected_rank


def test_compare_scores(valid_record_dict, base_policy):
    r1 = KnowledgeCard.from_dict(valid_record_dict)

    dict2 = valid_record_dict.copy()
    dict2["card_id"] = "test-456"
    dict2["validation_state"] = "VALID"
    r2 = KnowledgeCard.from_dict(dict2)

    f1 = extract_features(r1)
    f2 = extract_features(r2, {"evidence_verified": True})

    s1 = score(f1, base_policy, r1.card_id)
    s2 = score(f2, base_policy, r2.card_id)

    diff = compare_scores(s1, s2)
    assert "final_score_diff" in diff
    assert diff["final_score_diff"] < 0
    assert diff["dimension_diffs"]["evidence_strength"] < 0

def test_explain(valid_record_dict, base_policy):
    record = KnowledgeCard.from_dict(valid_record_dict)
    features = extract_features(record)
    score_card = score(features, base_policy, record.card_id)

    from core.solomon_knowledge_cards.scoring.engine import explain
    explanation = explain(score_card.score_id)
    assert "Base score" in explanation

    # Test missing
    assert "not found" in explain("non-existent-id")
