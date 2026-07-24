import os
import json
import tempfile
import pytest
from solomon_knowledge_cards import MnemosyneRuntime
from solomon_knowledge_cards.runtime import get_dynamic_context_budget
from solomon_knowledge_cards.embeddings import SemanticEmbedder
from solomon_knowledge_cards.graph_engine import KnowledgeGraph
from solomon_knowledge_cards.resource_monitor import get_scaled_memory_cap

@pytest.fixture
def temp_db():
    """Fixture that initializes a clean temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def runtime_test(temp_db):
    """Fixture providing a MnemosyneRuntime bound to the temporary database."""
    return MnemosyneRuntime(db_path=temp_db)


# --- 1. Dynamic Context & Advanced Embeddings Tests ---

def test_dynamic_context_budgets():
    """Verify that dynamic context budgets adjust based on active model targets."""
    # Test gpt-4o
    os.environ["SOLOMON_MODEL"] = "gpt-4o"
    assert get_dynamic_context_budget() == 64000

    # Test gpt-3.5
    os.environ["SOLOMON_MODEL"] = "gpt-3.5-turbo"
    assert get_dynamic_context_budget() == 16000

    # Test llama/local
    os.environ["SOLOMON_MODEL"] = "local-llama-3"
    assert get_dynamic_context_budget() == 12000

    # Clean up env
    if "SOLOMON_MODEL" in os.environ:
        del os.environ["SOLOMON_MODEL"]


def test_concept_projector_embeddings():
    """Verify that the Concept Projection vectorizer produces semantic alignments and matches expectations."""
    embedder = SemanticEmbedder()

    # Text with sports concept keywords
    sports_text = "Highly predictive sports odds betting arbitrage."
    # Text with database concept keywords
    db_text = "SQLite database table schema migration query."

    v_sports = embedder.get_embedding(sports_text)
    v_db = embedder.get_embedding(db_text)

    assert len(v_sports) == 128
    assert len(v_db) == 128

    # Cosine similarity between two unrelated concept texts should be low
    sim = embedder.cosine_similarity(v_sports, v_db)
    assert sim < 0.40

    # Similarity with itself should be exactly 1.0
    assert abs(embedder.cosine_similarity(v_sports, v_sports) - 1.0) < 1e-6


# --- 2. Knowledge Graph & Topological Sort Tests ---

def test_knowledge_graph_topological_sort(runtime_test):
    """Verify that Kahn's algorithm resolves prerequisites topologically (dependencies first)."""
    # Create 3 cards: Card A, Card B (which depends on A), and Card C (which depends on B)
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES
            ('KC-A', 'PROCEDURE', 'Card A', 'Prerequisite', 'Do A first.', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-B', 'PROCEDURE', 'Card B', 'Mid step', 'Do B second.', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-C', 'PROCEDURE', 'Card C', 'Final step', 'Do C last.', 'ACTIVE', 'PUBLIC', '[]', 'now', 'now')
        """)

    # Establish link dependencies: B depends on A, C depends on B
    runtime_test.add_card_link("KC-B", "KC-A", "DEPENDS_ON")
    runtime_test.add_card_link("KC-C", "KC-B", "DEPENDS_ON")

    graph = KnowledgeGraph(runtime_test)
    topo = graph.resolve_topology()

    # The topological sorted order must place prerequisites first: KC-A must come before KC-B, and KC-B before KC-C!
    idx_a = topo.index("KC-A")
    idx_b = topo.index("KC-B")
    idx_c = topo.index("KC-C")

    assert idx_a < idx_b
    assert idx_b < idx_c


# --- 3. Pre-emptive Safeguards & Auto-Financing Tests ---

def test_preemptive_safeguards_injection(runtime_test):
    """Verify that semantically linked FAILURE or REPAIR cards are successfully retrieved as safeguards."""
    # Create an active procedure card and a linked failure card
    conn = runtime_test.db.get_connection()
    with conn:
        conn.execute("""
            INSERT INTO knowledge_cards (card_id, card_type, title, summary, body, validation_state, security_classification, source_ids, created_at, updated_at)
            VALUES
            ('KC-PROC-SQL', 'PROCEDURE', 'SQL execute flow', 'Database procedure', 'Query execution details.', 'APPROVED', 'PUBLIC', '[]', 'now', 'now'),
            ('KC-FAIL-SQL', 'FAILURE', 'SQL injection risk', 'Database failure', 'Vulnerable to dynamic string injections. Fix: use parameters.', 'APPROVED', 'PUBLIC', '[]', 'now', 'now')
        """)

    # Link the FAILURE card to the PROCEDURE card
    runtime_test.add_card_link("KC-FAIL-SQL", "KC-PROC-SQL", "DEPENDS_ON")

    graph = KnowledgeGraph(runtime_test)
    safeguards = graph.get_failure_safeguards_for_query(query="execute flow", clearance="PUBLIC")

    # The linked FAILURE card must be correctly resolved as a pre-emptive safeguard!
    assert len(safeguards) == 1
    assert safeguards[0]["card_id"] == "KC-FAIL-SQL"
    assert "use parameters" in safeguards[0]["body"]


def test_auto_financing_ram_cap_scaling(runtime_test):
    """Verify that memory cap dynamically scales up in proportion to Loki's net betting profit."""
    # Initial state (no bets, profit = 0) -> should return base cap 1536MB
    assert get_scaled_memory_cap() == 1536.0

    # Seed some winning bets to generate profit
    conn = runtime_test.db.get_connection()
    with conn:
        # Create loki_bankroll table and insert initial default
        conn.execute("""
            INSERT INTO loki_bets (bet_id, sport, fixture, market, outcome, odds, shin_prob, kelly_fraction, stake, status, profit_loss, created_at)
            VALUES
            ('bet-win-1', 'Premier League', 'Manchester Utd vs Chelsea', 'Moneyline', 'Draw', 3.20, 0.35, 0.05, 100.0, 'WON', 220.0, 'now'),
            ('bet-win-2', 'NBA', 'Lakers vs Celtics', 'Moneyline', 'Lakers Win', 1.90, 0.55, 0.08, 200.0, 'WON', 180.0, 'now')
        """)
        # Total profit = 220 + 180 = $400.00

    # Set temporary environment override for DB path so the global get_scaled_memory_cap queries this test database
    os.environ["SOLOMON_DB_PATH"] = runtime_test.db_path

    # We added scaled_cap = base_cap + (net_profit * 1.0)
    # Expected: 1536.0 + (400.0 * 1.0) = 1936.0 MB!
    scaled_cap = get_scaled_memory_cap()
    assert scaled_cap == 1936.0

    # Seed extreme profit to trigger the 3.0GB (3072MB) maximum ceiling
    with conn:
        conn.execute("""
            INSERT INTO loki_bets (bet_id, sport, fixture, market, outcome, odds, shin_prob, kelly_fraction, stake, status, profit_loss, created_at)
            VALUES ('bet-jackpot', 'NFL', 'Super Bowl', 'Moneyline', 'Chiefs', 5.0, 0.50, 0.10, 1000.0, 'WON', 4000.0, 'now')
        """)

    # Expected: 1536 + 4400 = 5936 -> capped at maximum 3072.0 MB!
    assert get_scaled_memory_cap() == 3072.0

    if "SOLOMON_DB_PATH" in os.environ:
        del os.environ["SOLOMON_DB_PATH"]
