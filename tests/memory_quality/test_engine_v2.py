import pytest
import os
import datetime
from core.memory_quality.models import QualityDimensions, ScoringPolicy, ScoreExplanation, MemoryQualityScore
from core.memory_quality.engine import extract_features, score, rescore, compare_scores, explain
from core.memory_quality.repository import MemoryQualityRepository
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.memory_quality.adapter import adapt_card_confidence

@pytest.fixture
def test_db_path(tmp_path):
    db_file = tmp_path / "test_memory_quality.db"
    yield str(db_file)
    if db_file.exists():
        os.remove(db_file)

@pytest.fixture
def repository(test_db_path):
    db_manager = DatabaseManager(db_path=test_db_path)
    return MemoryQualityRepository(db_manager=db_manager)

@pytest.fixture
def sample_policy():
    return ScoringPolicy(
        version="v2.0.0",
        weights={
            "evidence": 2.0,
            "provenance": 1.5,
            "corroboration": 1.0,
            "specificity": 1.0,
            "novelty": 0.5,
            "utility": 1.0,
            "stability": 0.5,
            "contradiction_risk": 2.0
        },
        default_decay_rate=1.0,
        domain_decay_rates={"fast_moving": 2.0, "stable": 0.1},
        gates={
            "min_provenance": 0.2,
            "required_verification": ["VALID", "UNVALIDATED"],
            "max_contradiction_risk": 0.8
        }
    )

def test_extract_features():
    record = {
        "evidence": "A" * 500, # 1.0
        "source_type": "verified_human", # 1.0
        "related_card_ids": ["1", "2", "3", "4", "5"], # 1.0
        "body": "B" * 1000, # 1.0
        "updated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "parent_card_ids": [], # 1.0 novelty
        "validation_state": "VALID"
    }
    context = {
        "access_count": 100, # 1.0
        "update_count": 0, # 1.0
        "contradiction_risk": 0.0
    }

    features = extract_features(record, context)

    assert features.evidence == 1.0
    assert features.provenance == 1.0
    assert features.corroboration == 1.0
    assert features.specificity >= 1.0
    assert features.freshness == 1.0
    assert features.novelty == 1.0
    assert features.utility == 1.0
    assert features.stability == 1.0
    assert features.contradiction_risk == 0.0
    assert features.verification_status == "VALID"

def test_score_perfect(sample_policy):
    features = QualityDimensions(
        evidence=1.0, provenance=1.0, corroboration=1.0, specificity=1.0,
        freshness=1.0, novelty=1.0, utility=1.0, stability=1.0,
        contradiction_risk=0.0, verification_status="VALID"
    )

    explanation = score(features, sample_policy)

    assert explanation.gated is False
    assert explanation.base_score == 1.0
    assert explanation.decay_penalty == 0.0

def test_score_gated_provenance(sample_policy):
    features = QualityDimensions(
        evidence=1.0, provenance=0.1, # Below min_provenance=0.2
        corroboration=1.0, specificity=1.0,
        freshness=1.0, novelty=1.0, utility=1.0, stability=1.0,
        contradiction_risk=0.0, verification_status="VALID"
    )

    explanation = score(features, sample_policy)

    assert explanation.gated is True
    assert "Provenance" in explanation.gate_reason

def test_score_gated_verification(sample_policy):
    features = QualityDimensions(
        evidence=1.0, provenance=1.0,
        corroboration=1.0, specificity=1.0,
        freshness=1.0, novelty=1.0, utility=1.0, stability=1.0,
        contradiction_risk=0.0, verification_status="INVALID" # Not in ["VALID", "UNVALIDATED"]
    )

    explanation = score(features, sample_policy)

    assert explanation.gated is True
    assert "Verification status" in explanation.gate_reason

def test_score_decay_logic(sample_policy):
    features = QualityDimensions(
        evidence=1.0, provenance=1.0, corroboration=1.0, specificity=1.0,
        freshness=0.0, novelty=1.0, utility=1.0, stability=1.0,
        contradiction_risk=0.0, verification_status="VALID"
    )

    explanation_default = score(features, sample_policy)
    explanation_fast = score(features, sample_policy, domain="fast_moving")
    explanation_stable = score(features, sample_policy, domain="stable")

    assert explanation_fast.decay_penalty > explanation_default.decay_penalty
    assert explanation_default.decay_penalty > explanation_stable.decay_penalty

def test_repository_persistence(repository, sample_policy):
    score_obj = MemoryQualityScore(
        record_id="rec_123",
        policy_version="v2.0.0",
        final_score=0.85,
        features_snapshot=QualityDimensions(),
        explanation=ScoreExplanation(base_score=0.85, gated=False, dimension_contributions={})
    )

    repository.save_score(score_obj)

    retrieved = repository.get_score(score_obj.score_id)
    assert retrieved is not None
    assert retrieved.record_id == "rec_123"
    assert retrieved.final_score == 0.85
    assert retrieved.policy_version == "v2.0.0"

    history = repository.get_scores_for_record("rec_123")
    assert len(history) == 1

def test_adapter(repository, sample_policy):
    card = KnowledgeCard(
        card_id="c1", card_type="KNOWLEDGE", schema_version="1",
        title="Test Card", summary="Summary", body="Body",
        status="DRAFT", confidence=0.1, validation_state="VALID",
        created_at=datetime.datetime.now(datetime.UTC).isoformat(),
        updated_at=datetime.datetime.now(datetime.UTC).isoformat(),
        created_by="user", source_type="verified_human",
        source_ids=[], parent_card_ids=[], related_card_ids=[], tags=["domain:stable"],
        security_classification="U", evidence="Good evidence"
    )

    updated_card = adapt_card_confidence(card, sample_policy, repository)

    assert updated_card.confidence != 0.1 # Should have been updated
    assert updated_card.extra_metadata is not None
    assert "v2_score_id" in updated_card.extra_metadata

    score_id = updated_card.extra_metadata["v2_score_id"]
    explanation_dict = explain(score_id, repository)
    assert explanation_dict is not None
    assert explanation_dict["record_id"] == "c1"

def test_compare_scores():
    score_a = MemoryQualityScore(
        record_id="1", policy_version="v1", final_score=0.5,
        features_snapshot=QualityDimensions(evidence=0.5),
        explanation=ScoreExplanation(base_score=0.5, gated=False, dimension_contributions={})
    )
    score_b = MemoryQualityScore(
        record_id="1", policy_version="v2", final_score=0.8,
        features_snapshot=QualityDimensions(evidence=0.8),
        explanation=ScoreExplanation(base_score=0.8, gated=False, dimension_contributions={})
    )

    diff = compare_scores(score_a, score_b)
    assert abs(diff["final_score_diff"] - 0.3) < 1e-9
    assert diff["policy_version_change"] is True
    assert abs(diff["dimension_diffs"]["evidence"] - 0.3) < 1e-9

def test_calibration_fixture(sample_policy):
    # Tests a boundary ranking case where high verified novel card beats older unverified
    record1 = {
        "evidence": "A" * 1000,
        "source_type": "verified_human",
        "validation_state": "VALID",
        "updated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "parent_card_ids": [],
    }
    context1 = {"access_count": 50, "contradiction_risk": 0.0, "update_count": 0}

    record2 = {
        "evidence": "B" * 100,
        "source_type": "sensor",
        "validation_state": "VALID",
        "updated_at": (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=100)).isoformat(),
        "parent_card_ids": ["1", "2", "3", "4"], # less novelty
    }
    context2 = {"access_count": 10, "contradiction_risk": 0.1, "update_count": 5}

    features1 = extract_features(record1, context1)
    features2 = extract_features(record2, context2)

    score1 = score(features1, sample_policy)
    score2 = score(features2, sample_policy)

    assert score1.base_score > score2.base_score
    assert (score1.base_score - score1.decay_penalty) > (score2.base_score - score2.decay_penalty)
