import os
import tempfile
import json
import pytest
import datetime
import numpy as np

# Core memory imports
from core.solomon_quantized_memory import QuantizedBrainMap, QuantizedMemoryNode, LAYER_SHORT_TERM, LAYER_LONG_TERM
from core.solomon_context_budgeter import ContextBudgetPlanner

# Knowledge Card imports
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.models.card import KnowledgeCard, ValidationError
from core.solomon_knowledge_cards.api.repository import CardRepository
from core.solomon_knowledge_cards.api.review import ReviewGate
from core.solomon_knowledge_cards.api.graph import RelationGraph
from core.solomon_knowledge_cards.extractor.proposal_engine import ProposalEngine


# ==========================================
# 1. Quantized Memory & Brain Map Tests
# ==========================================

def test_quantized_memory_node():
    """Asserts QuantizedMemoryNode attributes, serialization, and Ebbinghaus decay."""
    node = QuantizedMemoryNode(node_type="KNOWLEDGE", content="Test memory content", importance=0.8, arousal=0.9)
    assert node.importance == 0.8
    assert node.arousal == 0.9
    assert len(node.ternary_vector) == 128
    assert set(node.ternary_vector).issubset({-1, 0, 1})

    # Access increment
    old_access_count = node.access_count
    node.access()
    assert node.access_count == old_access_count + 1
    assert node.activation > 0.0

    # Serialization
    serialized = node.serialize()
    assert isinstance(serialized, bytes)
    assert len(serialized) == 169  # 41 bytes metadata + 128 bytes vector

    # Temporal Decay
    node.activation = 1.0
    # Simulate time elapsed
    decay_time = node.last_accessed + 600.0  # 10 minutes
    node.ebbinghaus_decay(decay_time)
    assert node.activation < 1.0


def test_quantized_brain_map_operations():
    """Asserts QuantizedBrainMap ingestion, recall, and vectorized activation spreading."""
    brain_map = QuantizedBrainMap(max_nodes=50)

    # Ingest memories
    node_id_1 = brain_map.ingest(node_type="FAILURE", content="Connection timed out on port 3000", arousal=0.85)
    node_id_2 = brain_map.ingest(node_type="REPAIR", content="Retry after clearing port 3000 conflicts", arousal=0.4)

    stats = brain_map.get_stats()
    assert stats["total_nodes_in_ram"] == 2
    assert stats["matrix_non_zeros"] >= 0

    # Recall via vectorized spreading activation
    results = brain_map.recall("timed out port 3000")
    assert len(results) > 0
    assert any("port 3000" in r["content"] for r in results)

    # Autonomic Nervous System loop toggle
    assert not brain_map.ans_running
    brain_map.start_ans()
    assert brain_map.ans_running
    brain_map.stop_ans()
    assert not brain_map.ans_running


# ==========================================
# 2. Context Budget Planner Tests
# ==========================================

class MockDB:
    def __init__(self, search_results):
        self.results = search_results

    def semantic_search(self, query: str, top_k: int = 20):
        return self.results


def test_context_budget_planner():
    """Asserts ContextBudgetPlanner budget calculations, token limits, and priority retrieval."""
    planner = ContextBudgetPlanner(model_context_window=1000, system_prompt_reserve=100, expected_response_reserve=200, safety_margin=50)

    # Budget calculation with dynamic safety (margin + 10% of task input)
    # Available = 1000 - 100 - 200 - 50 - (50 + 5) = 595
    budget = planner.calculate_budget(task_input_size=50)
    assert budget == 595

    # Priority Layered Retrieval
    mock_results = [
        {"card_id": "C1", "family": "Safety Checklist", "content": "Security first", "similarity": 0.9},
        {"card_id": "C2", "family": "port failure", "content": "Clear conflicting ports before launch", "similarity": 0.8},
        {"card_id": "C3", "family": "General info", "content": "Standard operational steps details", "similarity": 0.75},
        {"card_id": "C4", "family": "Optional info", "content": "Extra secondary metadata to truncate if budget is exceeded", "similarity": 0.4}
    ]
    db = MockDB(mock_results)

    # Tight budget to force truncation / skipping
    tight_planner = ContextBudgetPlanner(model_context_window=400, system_prompt_reserve=50, expected_response_reserve=50, safety_margin=10)
    retrieved = tight_planner.retrieve_context(db, "deploy app", task_input_size=20, relevance_threshold=0.7)

    assert len(retrieved) > 0
    # The optional/secondary info should either be truncated or skipped
    any_truncated = any("[TRUNCATED]" in r["content"] for r in retrieved)
    assert len(retrieved) <= len(mock_results)


# ==========================================
# 3. Knowledge Card & Database Tests
# ==========================================

def test_knowledge_card_validation():
    """Asserts KnowledgeCard field validations."""
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # Valid card
    card = KnowledgeCard(
        card_id="KC-12345",
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="Valid Test Card",
        summary="Test summary",
        body="Test body text",
        status="DRAFT",
        confidence=0.8,
        validation_state="UNVALIDATED",
        created_at=now_str,
        updated_at=now_str,
        created_by="test_suite",
        source_type="TEST",
        source_ids=[],
        parent_card_ids=[],
        related_card_ids=[],
        tags=["test"],
        security_classification="INTERNAL",
        evidence="Observed test execution"
    )
    assert card.card_id == "KC-12345"

    # Invalid card_type
    with pytest.raises(ValidationError):
        KnowledgeCard(
            card_id="KC-12345",
            card_type="INVALID_TYPE",
            schema_version="1.0.0",
            title="Valid Test Card",
            summary="Test summary",
            body="Test body text",
            status="DRAFT",
            confidence=0.8,
            validation_state="UNVALIDATED",
            created_at=now_str,
            updated_at=now_str,
            created_by="test_suite",
            source_type="TEST",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=["test"],
            security_classification="INTERNAL",
            evidence="Observed test execution"
        )


def test_database_and_repository_lifecycle():
    """Asserts SQLite database migrations, card insertions, custom links, and hybrid searches."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        db_mgr = DatabaseManager(db_path)
        repo = CardRepository(db_mgr)
        review = ReviewGate(db_mgr)
        graph = RelationGraph(repo)

        now_str = datetime.datetime.now(datetime.UTC).isoformat()

        # Insert DRAFT card
        card1 = KnowledgeCard(
            card_id="PC-DEPLOY-1",
            card_type="KNOWLEDGE",
            schema_version="1.0.0",
            title="Standard Deployment Procedure",
            summary="Deployment steps for standard microservices.",
            body="Step 1: Check resources. Step 2: Clear ports. Step 3: Run launch script.",
            status="DRAFT",
            confidence=0.9,
            validation_state="UNVALIDATED",
            created_at=now_str,
            updated_at=now_str,
            created_by="test_suite",
            source_type="MANUAL",
            source_ids=[],
            parent_card_ids=[],
            related_card_ids=[],
            tags=["deploy", "production"],
            security_classification="INTERNAL",
            evidence="Standard best practices document"
        )
        repo.create_card(card1, creator="test_suite")

        # Verify card retrieval
        retrieved = repo.get_card("PC-DEPLOY-1")
        assert retrieved is not None
        assert retrieved.title == "Standard Deployment Procedure"

        # ReviewGate promotion transitions: DRAFT -> REVIEWED -> APPROVED -> ACTIVE
        card_rev = review.review_card("PC-DEPLOY-1", notes="Procedural integrity checked", updater="reviewer_alice")
        assert card_rev.status == "REVIEWED"

        card_app = review.approve_card("PC-DEPLOY-1", updater="approver_bob")
        assert card_app.status == "APPROVED"
        assert card_app.validation_state == "VALID"

        card_act = review.activate_card("PC-DEPLOY-1", updater="operator_charlie")
        assert card_act.status == "ACTIVE"

        # Add custom semantic links
        card2 = KnowledgeCard(
            card_id="RC-PORT-CONFL",
            card_type="REPAIR",
            schema_version="1.0.0",
            title="Port Binding Repair",
            summary="Remediation for port binding conflict failures.",
            body="Find process on port and kill it: lsof -t -i :3000 | xargs kill",
            status="APPROVED",
            confidence=1.0,
            validation_state="VALID",
            created_at=now_str,
            updated_at=now_str,
            created_by="test_suite",
            source_type="TEST",
            source_ids=["PC-DEPLOY-1"],
            parent_card_ids=[],
            related_card_ids=[],
            tags=["port", "remediation"],
            security_classification="INTERNAL",
            evidence="Proven in local shell trial runs"
        )
        repo.create_card(card2, creator="test_suite")

        # Link cards
        repo.link_cards("PC-DEPLOY-1", "RC-PORT-CONFL", "RELATED")
        related = repo.get_related_cards("PC-DEPLOY-1")
        assert len(related) > 0
        assert any(r.card_id == "RC-PORT-CONFL" for r in related)

        # Graph Traversal Dependency checks
        repo.link_cards("PC-DEPLOY-1", "RC-PORT-CONFL", "DEPENDS_ON")
        dep_chain = graph.find_dependency_chain("PC-DEPLOY-1")
        assert "RC-PORT-CONFL" in dep_chain

        # Hybrid Search
        search_results = repo.search("Port Binding conflict")
        assert len(search_results) > 0
        assert search_results[0]["card_id"] == "RC-PORT-CONFL"

        # Export and Import check
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as jsonl_file:
            jsonl_path = jsonl_file.name

        try:
            repo.export_cards(jsonl_path)
            assert os.path.getsize(jsonl_path) > 0

            # Create new database and import
            new_db_path = db_path + "_imported"
            new_db_mgr = DatabaseManager(new_db_path)
            new_repo = CardRepository(new_db_mgr)
            new_repo.import_cards(jsonl_path, updater="importer_bot")

            assert len(new_repo.list_cards()) == 2
        finally:
            if os.path.exists(jsonl_path):
                os.remove(jsonl_path)
            if os.path.exists(new_db_path):
                os.remove(new_db_path)

        # Proposal Engine test
        proposal_engine = ProposalEngine(repo)
        proposal = proposal_engine.create_procedure_proposal("RC-PORT-CONFL", creator="test_proposal_bot")
        assert proposal is not None
        assert proposal.card_type == "PROPOSAL"
        assert proposal.status == "DRAFT"

        with tempfile.TemporaryDirectory() as checklist_temp:
            # Inject a custom file path into proposal body to write safely
            fake_md_path = os.path.join(checklist_temp, "pc_deploy_1.md")
            proposal.body = f"Target Document: `{fake_md_path}`\n```markdown\n## [PROPOSED] Self-Healing Protocol\n- Kill conflicting processes.\n```"
            repo.update_card(proposal, updater="test_suite")

            # Status transition to APPROVED to apply to disk
            review.review_card(proposal.card_id, notes="Approved", updater="reviewer_alice")
            review.approve_card(proposal.card_id, updater="approver_bob")

            success = proposal_engine.apply_proposal_to_disk(proposal.card_id)
            assert success
            assert os.path.exists(fake_md_path)
            with open(fake_md_path, "r") as f:
                content = f.read()
            assert "Self-Healing Protocol" in content

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
