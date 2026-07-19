import os
import datetime
import pytest
from solomon_knowledge_cards.models.card import KnowledgeCard
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.api.graph import RelationGraph
from solomon_knowledge_cards.extractor.proposal_engine import ProposalEngine
from solomon_knowledge_cards.extractor.reflection import ReflectionSynthesizer

@pytest.fixture
def phase3b_services(tmp_path):
    db_file = tmp_path / "phase3b.db"
    db = DatabaseManager(str(db_file))
    repo = CardRepository(db)
    graph = RelationGraph(repo)
    proposal_eng = ProposalEngine(repo)
    reflection_eng = ReflectionSynthesizer(repo)
    return repo, graph, proposal_eng, reflection_eng

def test_hybrid_semantic_search(phase3b_services):
    repo, _, _, _ = phase3b_services
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # Create two cards
    card1 = KnowledgeCard(
        card_id="KC-HYB-1",
        card_type="KNOWLEDGE",
        schema_version="1.0.0",
        title="OpenHands setup timeout",
        summary="Common environment latency issues during launch.",
        body="Increasing setup times fixes this problem.",
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
        evidence="Observed locally",
        why_created="Why",
        problem_solved="Problem",
        future_work_dependent="Future"
    )
    repo.create_card(card1)

    # Retrieve and check that embedding exists in extra_metadata
    fetched = repo.get_card("KC-HYB-1")
    assert "embedding" in fetched.extra_metadata
    assert len(fetched.extra_metadata["embedding"]) == 128

    # Run a query search
    results = repo.search("timeout on openhands launch")
    assert len(results) == 1
    assert results[0]["card_id"] == "KC-HYB-1"
    # Match explanation must contain semantic similarity score
    assert "Semantic similarity" in results[0]["explanation"]

def test_graph_relation_and_dependencies(phase3b_services):
    repo, graph, _, _ = phase3b_services
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # Create cards
    card_a = KnowledgeCard(
        card_id="KC-A", card_type="KNOWLEDGE", schema_version="1.0.0", title="Card A", summary="S", body="B",
        status="ACTIVE", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=[],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    card_b = KnowledgeCard(
        card_id="KC-B", card_type="KNOWLEDGE", schema_version="1.0.0", title="Card B", summary="S", body="B",
        status="ACTIVE", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=[],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    card_c = KnowledgeCard(
        card_id="KC-C", card_type="KNOWLEDGE", schema_version="1.0.0", title="Card C", summary="S", body="B",
        status="ACTIVE", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=[],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repo.create_card(card_a)
    repo.create_card(card_b)
    repo.create_card(card_c)

    # Establish graph linkages: A depends on B, B depends on C
    repo.link_cards("KC-A", "KC-B", "DEPENDS_ON")
    repo.link_cards("KC-B", "KC-C", "DEPENDS_ON")

    # Retrieve dependency chain for KC-A
    chain = graph.find_dependency_chain("KC-A")
    # Expected topological resolution (C first, then B)
    assert chain == ["KC-C", "KC-B"]

    # 2. Test Circular Dependency Resolution
    # Link C depends on A (completing circle A -> B -> C -> A)
    repo.link_cards("KC-C", "KC-A", "DEPENDS_ON")
    # Search should terminate cleanly without stack overflow
    circular_chain = graph.find_dependency_chain("KC-A")
    assert len(circular_chain) <= 3

    # 3. Retrieve surrounding subgraph
    subgraph = graph.get_subgraph("KC-A", max_depth=2)
    assert len(subgraph["nodes"]) >= 2
    assert len(subgraph["edges"]) >= 2

def test_proposal_engine_dryrun_and_mutation(phase3b_services, tmp_path):
    repo, _, proposal_eng, _ = phase3b_services
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # Pre-register Procedure ID card to establish legacy doctrine record
    proc_card = KnowledgeCard(
        card_id="PC-DOCTRINE-E2E", card_type="SKILL", schema_version="1.0.0", title="Original procedure", summary="S", body="Original steps checklist",
        status="APPROVED", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=[],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future",
        extra_metadata={"original_file_path": str(tmp_path / "procedure.md")}
    )
    repo.create_card(proc_card)

    # Register a Repair Card referencing the procedure
    rep_card = KnowledgeCard(
        card_id="RC-99", card_type="REPAIR", schema_version="1.0.0", title="Fix setup errors", summary="S", body="Kill processes on port 3000",
        status="ACTIVE", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=["PC-DOCTRINE-E2E"], parent_card_ids=[], related_card_ids=[], tags=[],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repo.create_card(rep_card)

    # Create procedure proposal (dry-run)
    prop = proposal_eng.create_procedure_proposal("RC-99")
    assert prop is not None
    assert prop.card_type == "PROPOSAL"
    assert prop.status == "DRAFT"
    assert "PC-DOCTRINE-E2E" in prop.source_ids

    # Mutation should fail while in DRAFT status
    applied = proposal_eng.apply_proposal_to_disk(prop.card_id)
    assert applied is False

    # Approve and activate proposal
    prop.status = "APPROVED"
    repo.update_card(prop)

    # Mutation should succeed now!
    applied_success = proposal_eng.apply_proposal_to_disk(prop.card_id)
    assert applied_success is True

    # Read output markdown and verify it contains proposed section
    with open(tmp_path / "procedure.md", "r") as f:
        md_text = f.read()
    assert "[PROPOSED] Self-Healing Protocol" in md_text
    assert "Kill processes on port 3000" in md_text

def test_reflection_and_reinforcement_learning(phase3b_services):
    repo, _, _, reflection_eng = phase3b_services
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # Create two timeout failures to trigger reflection
    fail1 = KnowledgeCard(
        card_id="FC-TIMEOUT-1", card_type="FAILURE", schema_version="1.0.0", title="Pip setup timeout", summary="S", body="Encountered pip timeout in container launch.",
        status="DRAFT", confidence=0.8, validation_state="UNVALIDATED", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=["timeout"],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    fail2 = KnowledgeCard(
        card_id="FC-TIMEOUT-2", card_type="FAILURE", schema_version="1.0.0", title="Docker compose timeout", summary="S", body="Encountered docker compose timeout.",
        status="DRAFT", confidence=0.8, validation_state="UNVALIDATED", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=["timeout"],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repo.create_card(fail1)
    repo.create_card(fail2)

    # Synthesize research objectives
    researches = reflection_eng.analyze_failures_and_synthesize_research()
    assert len(researches) == 1
    res_card = researches[0]
    assert res_card.card_type == "RESEARCH"
    assert "timeout" in res_card.tags
    assert res_card.why_created == "To investigate and systematically resolve recurring failure patterns around 'timeout'."

    # 2. Test Reinforcement confidence adjustments
    repair_card = KnowledgeCard(
        card_id="RC-REINFORCE-1", card_type="REPAIR", schema_version="1.0.0", title="Test repair", summary="S", body="B",
        status="ACTIVE", confidence=0.6, validation_state="VALID", created_at=now_str, updated_at=now_str,
        created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=[],
        security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
    )
    repo.create_card(repair_card)

    # A. Successful run should increment confidence (+0.05)
    updated = reflection_eng.apply_reinforcement_feedback("RC-REINFORCE-1", was_successful=True)
    assert updated.confidence == 0.65

    # B. Failed runs should decay confidence (-0.10)
    decayed1 = reflection_eng.apply_reinforcement_feedback("RC-REINFORCE-1", was_successful=False)
    assert decayed1.confidence == 0.55

    # C. Severe confidence decay (< 0.3) should demote the card automatically to DRAFT/UNVALIDATED
    decayed2 = reflection_eng.apply_reinforcement_feedback("RC-REINFORCE-1", was_successful=False) # 0.45
    decayed3 = reflection_eng.apply_reinforcement_feedback("RC-REINFORCE-1", was_successful=False) # 0.35
    decayed4 = reflection_eng.apply_reinforcement_feedback("RC-REINFORCE-1", was_successful=False) # 0.25

    assert decayed4.confidence == 0.25
    assert decayed4.status == "DRAFT"
    assert decayed4.validation_state == "UNVALIDATED"
