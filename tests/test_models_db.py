import os
import datetime
import threading
import pytest
from solomon_knowledge_cards.models.card import KnowledgeCard, ValidationError
from solomon_knowledge_cards.storage.db import DatabaseManager

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_cards.db"
    return DatabaseManager(str(db_file))

def test_schema_validation():
    # 1. Valid card
    card = KnowledgeCard(
        card_id="KC-TEST-1",
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="Test Card",
        summary="A test card summary",
        body="This is the main body of the test knowledge card.",
        status="DRAFT",
        confidence=0.8,
        validation_state="UNVALIDATED",
        created_at="2026-07-19T12:00:00Z",
        updated_at="2026-07-19T12:00:00Z",
        created_by="tester",
        source_type="MANUAL",
        source_ids=["task-1"],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["test", "unit"],
        security_classification="INTERNAL",
        evidence="Observed test runs matching expected metrics",
        why_created="To test schema validation logic.",
        problem_solved="Prevents validation schema bypasses.",
        future_work_dependent="Ensures reliability of future database schema builds."
    )
    assert card.card_id == "KC-TEST-1"

    # 2. Invalid Card Type
    with pytest.raises(ValidationError, match="card_type must be one of"):
        KnowledgeCard(
            card_id="KC-TEST-1",
            card_type="INVALID_TYPE",
            schema_version="1.0.0",
            title="Test Card",
            summary="A test card summary",
            body="This is the main body of the test knowledge card.",
            status="DRAFT",
            confidence=0.8,
            validation_state="UNVALIDATED",
            created_at="2026-07-19T12:00:00Z",
            updated_at="2026-07-19T12:00:00Z",
            created_by="tester",
            source_type="MANUAL",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=[],
            security_classification="INTERNAL",
            evidence="Evidence"
        )

    # 3. Invalid Evidence Handling
    with pytest.raises(ValidationError, match="evidence is required and cannot be empty"):
        KnowledgeCard(
            card_id="KC-TEST-1",
            card_type="KNOWLEDGE",
            schema_version="1.0.0",
            title="Test Card",
            summary="A test card summary",
            body="This is the main body of the test knowledge card.",
            status="DRAFT",
            confidence=0.8,
            validation_state="UNVALIDATED",
            created_at="2026-07-19T12:00:00Z",
            updated_at="2026-07-19T12:00:00Z",
            created_by="tester",
            source_type="MANUAL",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=[],
            security_classification="INTERNAL",
            evidence=" "  # empty/whitespace
        )

    # 4. Invalid Timestamps
    with pytest.raises(ValidationError, match="Field created_at is not a valid ISO 8601 string"):
        KnowledgeCard(
            card_id="KC-TEST-1",
            card_type="KNOWLEDGE",
            schema_version="1.0.0",
            title="Test Card",
            summary="A test card summary",
            body="This is the main body of the test knowledge card.",
            status="DRAFT",
            confidence=0.8,
            validation_state="UNVALIDATED",
            created_at="July 19, 2026",
            updated_at="2026-07-19T12:00:00Z",
            created_by="tester",
            source_type="MANUAL",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=[],
            security_classification="INTERNAL",
            evidence="Some evidence."
        )

def test_db_create_read_update_delete(temp_db):
    now_str = datetime.datetime.now(datetime.UTC).isoformat()
    card = KnowledgeCard(
        card_id="KC-DB-1",
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="DB Test",
        summary="Testing DB operations",
        body="This card will be stored and updated.",
        status="DRAFT",
        confidence=0.9,
        validation_state="UNVALIDATED",
        created_at=now_str,
        updated_at=now_str,
        created_by="db_tester",
        source_type="TEST",
        source_ids=["src-1"],
        parent_card_ids=["parent-1"],
        related_card_ids=["rel-1"],
        tags=["database", "crud"],
        security_classification="INTERNAL",
        evidence="Tested via sqlite backend",
        why_created="To verify database schema insertion.",
        problem_solved="Ensures transactional writing works.",
        future_work_dependent="Bedrock of persistency."
    )

    # 1. Store
    temp_db.store_card(card, updater="db_tester", reason="Initial insertion")

    # 2. Read
    fetched = temp_db.get_card("KC-DB-1")
    assert fetched is not None
    assert fetched.card_id == "KC-DB-1"
    assert fetched.title == "DB Test"
    assert sorted(fetched.tags) == sorted(["database", "crud"])
    assert sorted(fetched.parent_card_ids) == ["parent-1"]
    assert sorted(fetched.related_card_ids) == ["rel-1"]
    assert fetched.why_created == "To verify database schema insertion."

    # 3. Update (preserving ID, checking revision history)
    card.title = "DB Test Updated"
    card.updated_at = datetime.datetime.now(datetime.UTC).isoformat()
    temp_db.store_card(card, updater="db_tester", reason="Updated title")

    fetched_updated = temp_db.get_card("KC-DB-1")
    assert fetched_updated.title == "DB Test Updated"

    # Check Revision History
    revisions = temp_db.get_revision_history("KC-DB-1")
    assert len(revisions) == 2
    assert revisions[0]["revision_number"] == 1
    assert revisions[0]["reason"] == "Initial insertion"
    assert revisions[1]["revision_number"] == 2
    assert revisions[1]["reason"] == "Updated title"
    assert revisions[1]["serialized_card"]["title"] == "DB Test Updated"

    # 4. Soft Delete / Deprecate
    success = temp_db.soft_delete_card("KC-DB-1", updater="db_tester", reason="Test soft delete")
    assert success is True

    # Reading without include_deleted=True should return None
    assert temp_db.get_card("KC-DB-1") is None
    # Reading with include_deleted=True should return deprecated card
    deleted_fetched = temp_db.get_card("KC-DB-1", include_deleted=True)
    assert deleted_fetched is not None
    assert deleted_fetched.status == "DEPRECATED"

def test_backup_and_recovery(temp_db, tmp_path):
    now_str = datetime.datetime.now(datetime.UTC).isoformat()
    card1 = KnowledgeCard(
        card_id="KC-BKP-1",
        card_type="DECISION",
        schema_version="1.0.0",
        title="Backup decision 1",
        summary="First backup card",
        body="Body details 1",
        status="ACTIVE",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="backup_manager",
        source_type="SYSTEM",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["backup"],
        security_classification="INTERNAL",
        evidence="Verified active schema version.",
        why_created="To assert reliable system recovery.",
        problem_solved="Mitigates data corruption risks.",
        future_work_dependent="Continuous runtime operations."
    )
    temp_db.store_card(card1)

    # Export to JSONL
    backup_file = tmp_path / "export.jsonl"
    temp_db.export_to_jsonl(str(backup_file))
    assert os.path.exists(backup_file)

    # Spin up an entirely new/clean database and restore
    recovery_db_file = tmp_path / "recovery.db"
    recovery_db = DatabaseManager(str(recovery_db_file))

    assert recovery_db.get_card("KC-BKP-1") is None

    # Import from JSONL
    recovery_db.import_from_jsonl(str(backup_file))
    restored = recovery_db.get_card("KC-BKP-1")
    assert restored is not None
    assert restored.card_id == "KC-BKP-1"
    assert restored.title == "Backup decision 1"
    assert restored.status == "ACTIVE"

def test_concurrent_write_behavior(temp_db):
    """Verifies that the DatabaseManager is thread-safe and concurrent writes do not corrupt SQLite."""
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    def write_worker(worker_id):
        card = KnowledgeCard(
            card_id=f"KC-CONCUR-{worker_id}",
            card_type="KNOWLEDGE",
            schema_version="1.0.0",
            title=f"Worker {worker_id} card",
            summary="concurrency test",
            body="body",
            status="DRAFT",
            confidence=0.5,
            validation_state="UNVALIDATED",
            created_at=now_str,
            updated_at=now_str,
            created_by=f"worker_{worker_id}",
            source_type="THREAD",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=["concurrency"],
            security_classification="INTERNAL",
            evidence="Concurrent thread launch",
            why_created="Why",
            problem_solved="Problem",
            future_work_dependent="Future"
        )
        temp_db.store_card(card, updater=f"thread_{worker_id}")

    threads = []
    for i in range(10):
        t = threading.Thread(target=write_worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify all 10 cards exist
    cards = temp_db.list_all_cards()
    assert len(cards) == 10
    ids = {c.card_id for c in cards}
    for i in range(10):
        assert f"KC-CONCUR-{i}" in ids
