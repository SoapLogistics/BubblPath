import pytest
import datetime
import json
import os
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.quality_engine.models import ScoringPolicy, MemoryFeatures, QualityScore
from core.solomon_knowledge_cards.quality_engine.extractor import extract_features
from core.solomon_knowledge_cards.quality_engine.scorer import score, explain, compare_scores
from core.solomon_knowledge_cards.quality_engine.batch_service import rescore
from core.solomon_knowledge_cards.quality_engine.adapter import apply_score_to_card

def create_mock_card(card_id, validation_state="VALID", evidence="Strong evidence here", tags=None, created_at=None, status="APPROVED"):
    if created_at is None:
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return KnowledgeCard(
        card_id=card_id,
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="Test Card",
        summary="A test card",
        body="This is the body of the test card. It is quite long enough to pass specificity tests, hopefully. Here is some more padding. " * 10,
        status=status,
        confidence=0.5,
        validation_state=validation_state,
        created_at=created_at,
        updated_at=created_at,
        created_by="test",
        source_type="test",
        source_ids=["src1"],
        parent_card_ids=[],
        related_card_ids=[],
        tags=tags or [],
        security_classification="UNCLASSIFIED",
        evidence=evidence
    )

def test_perfect_uncited_claim():
    # Perfect but uncited (no source_ids)
    card = create_mock_card("1")
    card.source_ids = []
    policy = ScoringPolicy()

    features = extract_features(card)
    assert features.provenance_reliability == 0.0 # Default when no sources (Fail closed)

    q_score = score(features, policy, card.card_id)
    # Provenance gate is 0.2, so 0.0 fails.
    assert q_score.gated_by == "provenance"
    assert q_score.final_score <= 0.4
    assert "GATED_BY_PROVENANCE" in q_score.reason_codes

def test_old_stable_fact():
    # Old, but stable and highly corroborated
    created_at = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=700)).isoformat()
    card = create_mock_card("2", created_at=created_at)
    card.related_card_ids = ["c1", "c2", "c3", "c4", "c5"]
    policy = ScoringPolicy()

    features = extract_features(card)
    assert features.freshness_days >= 700

    q_score = score(features, policy, card.card_id)
    # Decay should make freshness low
    assert q_score.components["freshness"] < 0.3

def test_rapidly_changing_fact():
    card = create_mock_card("3", tags=["fast-decay"])
    policy = ScoringPolicy()
    features = extract_features(card)
    assert features.domain == "fast_decay"

def test_frequently_retrieved_but_wrong():
    card = create_mock_card("4", validation_state="INVALID")
    card.extra_metadata = {"retrieval_count": 100}
    policy = ScoringPolicy()
    features = extract_features(card)
    q_score = score(features, policy, card.card_id)
    # Validation state is INVALID (0.0), gate is 0.1
    assert q_score.gated_by == "verification_status"
    assert q_score.final_score <= 0.4
    assert "GATED_BY_VERIFICATION_STATUS" in q_score.reason_codes

def test_verified_low_novelty():
    card = create_mock_card("5")
    policy = ScoringPolicy()
    features = extract_features(card, context={"novelty_score": 0.1})
    q_score = score(features, policy, card.card_id)
    assert q_score.components["novelty"] == 0.1
    assert q_score.final_score > 0.0 # should still have a decent score

def test_contradiction_penalties():
    card = create_mock_card("6")
    policy = ScoringPolicy()
    features = extract_features(card, context={"contradiction_risk": 0.9})
    q_score = score(features, policy, card.card_id)
    assert q_score.components["contradiction_risk"] == 0.9
    assert "HIGH_CONTRADICTION_RISK" in q_score.reason_codes

def test_policy_migrations_and_compare():
    card = create_mock_card("7")
    policy1 = ScoringPolicy(version="1.0.0")
    policy2 = ScoringPolicy(version="2.0.0")
    policy2.weights["evidence"] = 0.5

    features = extract_features(card)
    s1 = score(features, policy1, card.card_id)
    s2 = score(features, policy2, card.card_id)

    comp = compare_scores(s2, s1)
    assert comp["policy_transition"] == "1.0.0 -> 2.0.0"

def test_batch_rescore_and_adapter():
    c1 = create_mock_card("8")
    c2 = create_mock_card("9", validation_state="INVALID")
    policy = ScoringPolicy()

    results = rescore([c1, c2], policy)
    assert len(results) == 2

    apply_score_to_card(c1, results[c1.card_id])
    assert c1.confidence == results[c1.card_id].final_score
    assert c1.extra_metadata["latest_quality_score"]["score_id"] == results[c1.card_id].score_id
    assert len(c1.extra_metadata["quality_score_history"]) == 1

def test_calibration_fixtures():
    fixture_path = os.path.join("tests", "fixtures", "quality_calibration.json")
    assert os.path.exists(fixture_path), "Calibration fixture missing"

    with open(fixture_path, 'r') as f:
        cases = json.load(f)

    policy = ScoringPolicy()
    for case in cases:
        features = MemoryFeatures(**case["features"])
        q_score = score(features, policy, case["card_id"])

        if "expected_min_score" in case:
            assert q_score.final_score >= case["expected_min_score"]

        if "expected_max_score" in case:
            assert q_score.final_score <= case["expected_max_score"]

        if "expected_reason_codes" in case:
            for rc in case["expected_reason_codes"]:
                assert rc in q_score.reason_codes
