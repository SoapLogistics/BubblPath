import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from solomon_knowledge_cards.api.review import ReviewGate
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.models.card import KnowledgeCard

@pytest.fixture
def review_gate():
    fd, temp_db = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(temp_db)
    gate = ReviewGate(db)

    # Create a draft card
    card = KnowledgeCard(
        card_id="test_card",
        card_type="KNOWLEDGE",
        schema_version="1.0",
        title="Test",
        summary="Summary",
        body="Body",
        status="DRAFT",
        confidence=0.8,
        validation_state="UNVALIDATED",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        created_by="tester",
        source_type="test",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=[],
        security_classification="UNCLASSIFIED",
        evidence="Evidence"
    )
    db.store_card(card, updater="system", reason="Initial")

    yield gate, db
    os.remove(temp_db)

def test_review_gate_full_lifecycle(review_gate):
    gate, db = review_gate

    # DRAFT -> REVIEWED
    gate.review_card("test_card", notes="Looks good")
    card = db.get_card("test_card")
    assert card.status == "REVIEWED"
    assert card.extra_metadata["review_notes"] == "Looks good"

    # REVIEWED -> APPROVED
    gate.approve_card("test_card")
    card = db.get_card("test_card")
    assert card.status == "APPROVED"
    assert card.validation_state == "VALID"

    # APPROVED -> ACTIVE
    gate.activate_card("test_card")
    card = db.get_card("test_card")
    assert card.status == "ACTIVE"

def test_review_gate_rejection(review_gate):
    gate, db = review_gate

    gate.reject_card("test_card", reason="Needs work")
    card = db.get_card("test_card", include_deleted=True)
    assert card.status == "DEPRECATED"
    assert card.validation_state == "INVALID"

def test_review_gate_invalid_transition(review_gate):
    gate, db = review_gate

    # Cannot go DRAFT directly to ACTIVE
    with pytest.raises(ValueError):
        gate.activate_card("test_card")
