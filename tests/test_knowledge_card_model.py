import pytest
from core.solomon_knowledge_cards.models.card import KnowledgeCard, ValidationError

def test_knowledge_card_valid():
    card = KnowledgeCard(
        card_id="test_id",
        card_type="KNOWLEDGE",
        schema_version="1.0",
        title="Test Title",
        summary="Test Summary",
        body="Test Body",
        status="DRAFT",
        confidence=0.9,
        validation_state="VALID",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        created_by="tester",
        source_type="test",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=[],
        security_classification="UNCLASSIFIED",
        evidence="Test Evidence",
    )
    assert card.card_id == "test_id"

def test_knowledge_card_invalid_type():
    with pytest.raises(ValidationError):
        KnowledgeCard(
            card_id="test_id",
            card_type="INVALID_TYPE",
            schema_version="1.0",
            title="Test Title",
            summary="Test Summary",
            body="Test Body",
            status="DRAFT",
            confidence=0.9,
            validation_state="VALID",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            created_by="tester",
            source_type="test",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=[],
            security_classification="UNCLASSIFIED",
            evidence="Test Evidence",
        )

def test_knowledge_card_invalid_confidence():
    with pytest.raises(ValidationError):
        KnowledgeCard(
            card_id="test_id",
            card_type="KNOWLEDGE",
            schema_version="1.0",
            title="Test Title",
            summary="Test Summary",
            body="Test Body",
            status="DRAFT",
            confidence=1.5,
            validation_state="VALID",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            created_by="tester",
            source_type="test",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=[],
            security_classification="UNCLASSIFIED",
            evidence="Test Evidence",
        )

def test_knowledge_card_invalid_status():
    with pytest.raises(ValidationError):
        KnowledgeCard(
            card_id="test_id",
            card_type="KNOWLEDGE",
            schema_version="1.0",
            title="Test Title",
            summary="Test Summary",
            body="Test Body",
            status="INVALID_STATUS",
            confidence=0.9,
            validation_state="VALID",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            created_by="tester",
            source_type="test",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=[],
            security_classification="UNCLASSIFIED",
            evidence="Test Evidence",
        )

def test_knowledge_card_serialization():
    card = KnowledgeCard(
        card_id="test_id",
        card_type="KNOWLEDGE",
        schema_version="1.0",
        title="Test Title",
        summary="Test Summary",
        body="Test Body",
        status="DRAFT",
        confidence=0.9,
        validation_state="VALID",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        created_by="tester",
        source_type="test",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=[],
        security_classification="UNCLASSIFIED",
        evidence="Test Evidence",
    )
    data = card.to_dict()
    assert data["card_id"] == "test_id"

    card2 = KnowledgeCard.from_dict(data)
    assert card2.card_id == "test_id"
    assert card2.title == "Test Title"
