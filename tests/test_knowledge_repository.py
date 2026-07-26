import pytest
import os
import tempfile
import sys
# Add core to sys.path so the absolute imports in solomon_knowledge_cards work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.models.card import KnowledgeCard

@pytest.fixture
def repo():
    fd, temp_db = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(temp_db)
    repo = CardRepository(db)
    yield repo
    os.remove(temp_db)

def create_dummy_card(card_id, title="Test", card_type="KNOWLEDGE", tags=None, body="Body"):
    return KnowledgeCard(
        card_id=card_id,
        card_type=card_type,
        schema_version="1.0",
        title=title,
        summary="Summary",
        body=body,
        status="DRAFT",
        confidence=0.8,
        validation_state="VALID",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        created_by="tester",
        source_type="test",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=tags or [],
        security_classification="UNCLASSIFIED",
        evidence="Evidence"
    )

def test_repository_create_and_get(repo):
    card = create_dummy_card("test_id")
    repo.create_card(card, "tester", "Testing creation")

    retrieved = repo.get_card("test_id")
    assert retrieved is not None
    assert retrieved.card_id == "test_id"
    assert retrieved.title == "Test"

def test_repository_list_and_search(repo):
    repo.create_card(create_dummy_card("c1", title="First", card_type="KNOWLEDGE", tags=["t1"]), "tester")
    repo.create_card(create_dummy_card("c2", title="Second", card_type="LESSON", tags=["t2"]), "tester")

    cards = repo.list_cards()
    assert len(cards) == 2

    lessons = repo.search_by_type("LESSON")
    assert len(lessons) == 1
    assert lessons[0].card_id == "c2"

    t1_cards = repo.search_by_tags(["t1"])
    assert len(t1_cards) == 1
    assert t1_cards[0].card_id == "c1"

def test_repository_search_query(repo):
    repo.create_card(create_dummy_card("c1", title="Apples and Oranges", body="fruits"), "tester")
    repo.create_card(create_dummy_card("c2", title="Cars and Trucks", body="vehicles"), "tester")

    results = repo.search("apples")
    assert len(results) >= 1
    assert results[0]["card_id"] == "c1"

def test_repository_soft_delete(repo):
    repo.create_card(create_dummy_card("c1"), "tester")
    repo.deprecate_card("c1", "tester", "obsolete")

    # Should not appear in normal list
    cards = repo.list_cards()
    assert len(cards) == 0

    # Should appear if include_deleted=True
    all_cards = repo.list_cards(include_deleted=True)
    assert len(all_cards) == 1
    assert all_cards[0].status == "DEPRECATED"
