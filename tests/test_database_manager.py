import os
import sys
import sqlite3

# Dynamically add the core directory to sys.path so nested imports resolve correctly
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from core.solomon_knowledge_cards.storage.db import DatabaseManager

def test_database_manager_migrations(tmp_path):
    """
    Tests that DatabaseManager initializes and correctly applies migrations up to version 3.
    """
    db_file = os.path.join(tmp_path, "test_solomon_state.db")

    # Initialize database manager
    db = DatabaseManager(db_path=db_file)

    # Connect directly and query the applied schema version and tables
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Assert schema version is 3
    cursor.execute("SELECT MAX(version) FROM schema_version")
    max_ver = cursor.fetchone()[0]
    assert max_ver == 3, f"Expected schema version 3, got {max_ver}"

    # 2. Assert that all 13 new tables exist
    expected_tables = [
        "system_events",
        "learning_candidates",
        "memories",
        "memory_links",
        "retrieval_traces",
        "memory_uses",
        "task_outcomes",
        "memory_outcomes",
        "governance_events",
        "resident_leases",
        "resident_checkpoints",
        "learning_targets",
        "evidence_artifacts"
    ]

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row["name"] for row in cursor.fetchall()]

    for t in expected_tables:
        assert t in tables, f"Expected table {t} was not found in schema!"

    conn.close()
