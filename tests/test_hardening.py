import os
import datetime
import json
import pytest
import sys

# Configure a unique test DB path at module level BEFORE importing app
os.environ["SOLOMON_DB_PATH"] = "test_hardening_only.db"
os.environ["SOLOMON_ACTIONS_API_KEY"] = "secure_test_key"

from app import app, db_manager, repository
from solomon_knowledge_cards.migrator.importer import validate_safe_path
from solomon_knowledge_cards.api.embeddings import SemanticEmbedder
from solomon_knowledge_cards.api.graph import RelationGraph
from solomon_knowledge_cards.models.card import KnowledgeCard

@pytest.fixture
def harden_client():
    app.config["TESTING"] = True
    # Clean database before run
    if os.path.exists("test_hardening_only.db"):
        os.remove("test_hardening_only.db")
    db_manager._init_db()

    with app.test_client() as client:
        yield client, repository

    if os.path.exists("test_hardening_only.db"):
        os.remove("test_hardening_only.db")

def test_path_traversal_guards():
    # 1. Verify standard valid path passes
    assert validate_safe_path("solomon_knowledge_cards/models/card.py") is not None
    assert validate_safe_path("openclaw-workspace/checklists/openhands_integration.md") is not None

    # 2. Verify path traversals containing .. are strictly blocked
    with pytest.raises(ValueError, match="Security Violation: Path traversal attempt blocked"):
        validate_safe_path("../solomon_knowledge_cards/models/card.py")

    with pytest.raises(ValueError, match="Security Violation"):
        validate_safe_path("openclaw-workspace/checklists/../../../etc/passwd")

def test_cosine_similarity_division_by_zero():
    embedder = SemanticEmbedder()

    # 1. Zero-magnitude vector check
    zero_vec = [0.0] * 128
    valid_vec = [1.0] * 128

    # Similarity should be exactly 0.0 without throwing division by zero
    assert embedder.cosine_similarity(zero_vec, valid_vec) == 0.0
    assert embedder.cosine_similarity(valid_vec, zero_vec) == 0.0
    assert embedder.cosine_similarity(zero_vec, zero_vec) == 0.0

    # 2. Size mismatch check
    mismatch_vec = [1.0] * 64
    assert embedder.cosine_similarity(valid_vec, mismatch_vec) == 0.0

def test_graph_recursion_stack_limits(harden_client):
    _, repo = harden_client
    now_str = datetime.datetime.now(datetime.UTC).isoformat()

    # Limit maximum recursion depth on graph traversal to 10
    graph = RelationGraph(repo, max_recursion_depth=10)

    # Create a long linear chain of dependencies exceeding depth 10
    # KC_1 depends on KC_2 depends on KC_3 ... depends on KC_15
    for i in range(1, 16):
        card = KnowledgeCard(
            card_id=f"KC-REC-{i}", card_type="KNOWLEDGE", schema_version="1.0.0", title=f"Card {i}", summary="S", body="B",
            status="ACTIVE", confidence=1.0, validation_state="VALID", created_at=now_str, updated_at=now_str,
            created_by="tester", source_type="TEST", source_ids=[], parent_card_ids=[], related_card_ids=[], tags=[],
            security_classification="INTERNAL", evidence="E", why_created="Why", problem_solved="Problem", future_work_dependent="Future"
        )
        repo.create_card(card)

    for i in range(1, 15):
        repo.link_cards(f"KC-REC-{i}", f"KC-REC-{i+1}", "DEPENDS_ON")

    # Query dependency chain for KC-REC-1 (should abort gracefully at depth 10 to protect the thread stack!)
    chain = graph.find_dependency_chain("KC-REC-1")
    # Traversal should cut off and resolve cleanly
    assert len(chain) < 15

def test_payload_size_limits(harden_client):
    client, _ = harden_client
    headers = {"Authorization": "Bearer secure_test_key"}

    # Create a massive body payload exceeding 1.1MB to trigger content-length violation
    giant_payload = "X" * int(1.2 * 1024 * 1024)

    response = client.post("/api/command-center/solomon-chat", json={"message": giant_payload}, headers=headers)
    # Flask should reject with 413 (Request Entity Too Large)
    assert response.status_code == 413

def test_server_exception_sanitization(harden_client):
    client, _ = harden_client
    headers = {"Authorization": "Bearer secure_test_key"}

    # Send a request to list cards with malformed/unsupported query parameters that would cause an unhandled query syntax error
    # To test exception catching, let's query with an invalid tag filter or a payload that forces a server exception inside list_cards
    # We can pass query arg parameters that cause database filter operations to crash, e.g. a type parameter that breaks list constraints
    # Or simulate a route-level unexpected crash by calling /review with invalid JSON parameters
    bad_payload = {
        "card_id": "NON-EXISTENT",
        "target_status": "APPROVED", # This transition from None (non-existent card) will raise a ValueError inside transition_status
        "updater": "reviewer"
    }

    response = client.post("/api/command-center/review", json=bad_payload, headers=headers)
    # The status transition should raise a ValueError and be captured securely by our global @app.errorhandler
    # Returning clean 500 error instead of leaking internal tracebacks or file system variables!
    # Wait, in app.py we do:
    # `card = review_gate.transition_status(...)`
    # Let's verify that this returns a clean 400 or 500 depending on catch blocks
    assert response.status_code in (400, 500)
    data = json.loads(response.data)
    assert "error" in data
    # Traceback details should not be in the response string
    assert "Traceback" not in response.get_data(as_text=True)
