import pytest
import datetime
import os
import tempfile
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.api.repository import CardRepository
from core.solomon_knowledge_cards.api.review import ReviewGate

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    db = DatabaseManager(path)
    yield db
    os.unlink(path)

@pytest.fixture
def repo(temp_db):
    return CardRepository(temp_db)

@pytest.fixture
def review_gate(temp_db):
    return ReviewGate(temp_db)

def create_mock_card(card_id: str, title: str, status: str = "DRAFT") -> KnowledgeCard:
    return KnowledgeCard(
        card_id=card_id,
        card_type="KNOWLEDGE",
        schema_version="1.0",
        title=title,
        summary="A summary of the card",
        body="Detailed content of the knowledge card.",
        status=status,
        confidence=0.9,
        validation_state="UNVALIDATED",
        created_at=datetime.datetime.now(datetime.UTC).isoformat(),
        updated_at=datetime.datetime.now(datetime.UTC).isoformat(),
        created_by="test_user",
        source_type="test",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["test"],
        security_classification="PUBLIC",
        evidence="Tested successfully",
        why_created="testing",
        problem_solved="none",
        future_work_dependent="none"
    )

def test_knowledge_card_searchable(repo):
    card = create_mock_card("card1", "The Secret of the Universe")
    repo.create_card(card)

    results = repo.search("Universe")
    assert len(results) > 0
    assert results[0]["card_id"] == "card1"

def test_related_cards_linked(repo):
    card1 = create_mock_card("card1", "Card 1")
    card2 = create_mock_card("card2", "Card 2")
    repo.create_card(card1)
    repo.create_card(card2)

    # Test new relations
    repo.link_cards("card1", "card2", "DEPENDS_ON")
    repo.link_cards("card2", "card1", "VALIDATES")

    card3 = create_mock_card("card3", "Card 3")
    repo.create_card(card3)
    repo.link_cards("card3", "card1", "DERIVED_FROM")

    retrieved_card3 = repo.get_card("card3")
    links3 = retrieved_card3.extra_metadata.get("links", [])
    assert any(l["target_id"] == "card1" and l["link_type"] == "DERIVED_FROM" for l in links3)

    retrieved_card1 = repo.get_card("card1")
    links1 = retrieved_card1.extra_metadata.get("links", [])
    assert any(l["target_id"] == "card2" and l["link_type"] == "DEPENDS_ON" for l in links1)

    retrieved_card2 = repo.get_card("card2")
    links2 = retrieved_card2.extra_metadata.get("links", [])
    assert any(l["target_id"] == "card1" and l["link_type"] == "VALIDATES" for l in links2)

def test_retrieval_returns_relevant_results(repo):
    card1 = create_mock_card("card1", "Quantum Physics Basics")
    card2 = create_mock_card("card2", "Baking a Cake")
    repo.create_card(card1)
    repo.create_card(card2)

    results = repo.search("Quantum")
    assert len(results) > 0
    assert results[0]["card_id"] == "card1"

def test_invalid_memories_quarantined(repo, review_gate):
    card = create_mock_card("card1", "Bad Memory", status="DRAFT")
    repo.create_card(card)

    review_gate.reject_card("card1", reason="Completely false")

    retrieved = repo.get_card("card1", include_deleted=True)
    assert retrieved.status == "DEPRECATED"
    assert retrieved.validation_state == "INVALID"

def test_version_history_preserved(repo):
    card = create_mock_card("card1", "Initial Title")
    repo.create_card(card)

    card.title = "Updated Title"
    repo.update_card(card)

    history = repo.retrieve_revision_history("card1")
    assert len(history) == 2
    assert history[0]["serialized_card"]["title"] == "Initial Title"
    assert history[1]["serialized_card"]["title"] == "Updated Title"
