import os
import datetime
import pytest
from solomon_knowledge_cards.models.card import KnowledgeCard
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.extractor.extractor import KnowledgeExtractor
from solomon_knowledge_cards.api.review import ReviewGate

@pytest.fixture
def repo_and_services(tmp_path):
    db_file = tmp_path / "integration.db"
    db = DatabaseManager(str(db_file))
    repo = CardRepository(db)
    review_gate = ReviewGate(db)
    extractor = KnowledgeExtractor()
    return repo, review_gate, extractor

def test_search_ranking_and_security_filtering(repo_and_services):
    repo, _, _ = repo_and_services
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # Insert card 1: Match in Title
    card1 = KnowledgeCard(
        card_id="KC-SRC-1",
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="OpenHands timeout remediation playbook",
        summary="A generic summary",
        body="Body with no special keyword",
        status="ACTIVE",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="tester",
        source_type="TEST",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["timeout"],
        security_classification="INTERNAL",
        evidence="Evidence",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future"
    )
    # Insert card 2: Match only in Body (lower weight)
    card2 = KnowledgeCard(
        card_id="KC-SRC-2",
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="Generic title",
        summary="Generic summary",
        body="This body mentions OpenHands timeout error details.",
        status="ACTIVE",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="tester",
        source_type="TEST",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=[],
        security_classification="RESTRICTED",
        evidence="Evidence",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future"
    )

    repo.create_card(card1)
    repo.create_card(card2)

    # 1. Test Search Ranking: Query "OpenHands timeout"
    results = repo.search("OpenHands timeout")
    assert len(results) == 2
    # card1 must be ranked higher since it matched in the Title (weight 10 vs body weight 2)
    assert results[0]["card_id"] == "KC-SRC-1"
    assert results[1]["card_id"] == "KC-SRC-2"
    assert "Lexical Title matches" in results[0]["explanation"]
    assert "Lexical Body matches" in results[1]["explanation"]

    # 2. Test Security Classification Filtering
    restricted_results = repo.search("OpenHands timeout", security_classification="RESTRICTED")
    assert len(restricted_results) == 1
    assert restricted_results[0]["card_id"] == "KC-SRC-2"

def test_relationship_linking(repo_and_services):
    repo, _, _ = repo_and_services
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    card_p = KnowledgeCard(
        card_id="PC-PARENT",
        card_type="SKILL",
        schema_version="1.0.0",
        title="Parent Skill Card",
        summary="Summary",
        body="Body",
        status="ACTIVE",
        confidence=1.0,
        validation_state="VALID",
        created_at=now_str,
        updated_at=now_str,
        created_by="tester",
        source_type="TEST",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=[],
        security_classification="INTERNAL",
        evidence="Evidence",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future"
    )
    card_c = KnowledgeCard(
        card_id="KC-CHILD",
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="Child Knowledge Card",
        summary="Summary",
        body="Body",
        status="DRAFT",
        confidence=0.8,
        validation_state="UNVALIDATED",
        created_at=now_str,
        updated_at=now_str,
        created_by="tester",
        source_type="TEST",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=[],
        security_classification="INTERNAL",
        evidence="Evidence",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future"
    )

    repo.create_card(card_p)
    repo.create_card(card_c)

    # Link child to parent
    repo.link_cards("KC-CHILD", "PC-PARENT", "PARENT")

    # Fetch from DB and check links
    child_fetched = repo.get_card("KC-CHILD")
    assert child_fetched.parent_card_ids == ["PC-PARENT"]

    # Check related cards retrieval
    related = repo.get_related_cards("KC-CHILD")
    assert len(related) == 1
    assert related[0].card_id == "PC-PARENT"

def test_worker_report_extraction_and_review_gate(repo_and_services):
    repo, review_gate, extractor = repo_and_services

    # 1. Successful Worker Report
    success_report = {
        "task_id": "T-SUCCESS-99",
        "procedure_id": "PC-SO-01",
        "title": "Build compilation",
        "outcome": "success",
        "attempted": "Run standard pip installation and python build.",
        "succeeded": "All requirements installed successfully within 45s.",
        "failed": "None",
        "root_cause": "",
        "repair_action": "",
        "evidence": "Stdout logs showing 100% test pass on green build.",
        "tags": ["build", "python"]
    }

    success_cards = extractor.extract_draft_cards(success_report)
    assert len(success_cards) == 1
    less_card = success_cards[0]
    assert less_card.card_type == "LESSON"
    assert less_card.status == "DRAFT"
    assert less_card.validation_state == "UNVALIDATED"
    assert "extracted" in less_card.tags
    assert less_card.source_ids == ["T-SUCCESS-99", "PC-SO-01"]

    # 2. Store the draft card
    repo.create_card(less_card)

    # 3. Test Review Gate Transition (DRAFT -> REVIEWED)
    reviewed_card = review_gate.review_card(less_card.card_id, notes="Looks very clean. Recommended for approval.")
    assert reviewed_card.status == "REVIEWED"
    assert reviewed_card.extra_metadata["review_notes"] == "Looks very clean. Recommended for approval."

    # 4. Test Review Gate (REVIEWED -> APPROVED)
    approved_card = review_gate.approve_card(less_card.card_id)
    assert approved_card.status == "APPROVED"
    assert approved_card.validation_state == "VALID"

    # 5. Test Review Gate (APPROVED -> ACTIVE)
    active_card = review_gate.activate_card(less_card.card_id)
    assert active_card.status == "ACTIVE"

    # 6. Failure Worker Report
    failure_report = {
        "task_id": "T-FAIL-45",
        "procedure_id": "PC-AC-02",
        "title": "OpenHands API deployment",
        "outcome": "failure",
        "attempted": "Launch local docker instance of openhands API.",
        "succeeded": "Container startup",
        "failed": "Port binding on 3000 due to port conflicts",
        "root_cause": "Port 3000 was already occupied by background node service",
        "repair_action": "Kill existing process on port 3000: kill $(lsof -t -i :3000) or change openhands config port to 3001.",
        "evidence": "Docker-compose stdout error: Address already in use: 3000",
        "tags": ["docker", "openhands"]
    }

    draft_fails = extractor.extract_draft_cards(failure_report)
    # Should extract a FAILURE card and a REPAIR card
    assert len(draft_fails) == 2
    types = {c.card_type for c in draft_fails}
    assert "FAILURE" in types
    assert "REPAIR" in types

    for c in draft_fails:
        repo.create_card(c)

    fail_card = [c for c in draft_fails if c.card_type == "FAILURE"][0]
    repair_card = [c for c in draft_fails if c.card_type == "REPAIR"][0]

    assert repair_card.related_card_ids == [fail_card.card_id]

    # 7. Test Rejection
    rejected = review_gate.reject_card(fail_card.card_id, reason="This error is transient and was already fixed in main.")
    assert rejected.status == "DEPRECATED"
    assert rejected.validation_state == "INVALID"
    assert "rejected" in rejected.extra_metadata["status_change_reason"].lower()

def test_markdown_worker_report_extraction(repo_and_services):
    repo, _, extractor = repo_and_services

    markdown_report = """
# Worker Handover Report

### Task ID
T-MD-EXTRACT

### Procedure ID
PC-SO-99

### Outcome
failure

### Attempted
Compile python source code into a bundle.

### Succeeded
Parsed setup.py successfully.

### Failed
Building wheel file failed because of syntax errors.

### Root Cause
Missing trailing comma in setup.py options list.

### Repair Action
Add trailing comma to line 15 of setup.py and rerun build.

### Evidence
SyntaxError: invalid syntax on setup.py:15

### Tags
setup, compiler
"""
    draft_cards = extractor.extract_draft_cards(markdown_report)
    assert len(draft_cards) == 2
    fail_card = [c for c in draft_cards if c.card_type == "FAILURE"][0]
    repair_card = [c for c in draft_cards if c.card_type == "REPAIR"][0]

    assert fail_card.source_ids == ["T-MD-EXTRACT", "PC-SO-99"]
    assert fail_card.why_created == "To document the specific failure mode in task T-MD-EXTRACT associated with PC-SO-99."
    assert "setup" in fail_card.tags
    assert repair_card.related_card_ids == [fail_card.card_id]
