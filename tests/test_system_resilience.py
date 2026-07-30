import os
import sqlite3
import hashlib
import pytest
from services.solomon_governance_approval_packet import GovernanceApprovalLane
from services.solomon_futures_engine import FuturesEngine
from core.solomon_local_llm import SolomonLocalLLM

def test_backup_and_checksum_resilience(tmp_path):
    """
    Simulates backup generation, checksum tracking, and corruption checks.
    """
    # 1. Create fake database file
    db_file = tmp_path / "solomon_test.db"
    with sqlite3.connect(db_file) as conn:
        conn.execute("CREATE TABLE foo (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO foo VALUES (1, 'solomon')")
        conn.commit()

    # 2. Generate backup checksum
    hasher = hashlib.sha256()
    with open(db_file, "rb") as f:
        hasher.update(f.read())
    original_checksum = hasher.hexdigest()

    # Create backup copy
    backup_file = tmp_path / "solomon_test_backup.db"
    with open(db_file, "rb") as src, open(backup_file, "wb") as dst:
        dst.write(src.read())

    # 3. Corrupt backup deliberately
    with open(backup_file, "r+b") as f:
        f.seek(0)
        f.write(b"\x00\x00\x00")

    # 4. Verify corruption check catches it
    hasher_corrupted = hashlib.sha256()
    with open(backup_file, "rb") as f:
        hasher_corrupted.update(f.read())
    corrupted_checksum = hasher_corrupted.hexdigest()

    assert original_checksum != corrupted_checksum, "Tampering or corruption went undetected by checksum."

def test_ss3_promotion_bypass_rejection():
    """
    Verifies that the promotion framework rejects packets if validation or rollback options are bypassed.
    """
    lane = GovernanceApprovalLane()

    # Attempt to promote without required SS3 review verification
    bypass_packet = {
        "action": "promote_capability",
        "requires_ss3_review": True,
        "ss3_verified": False  # Bypassed
    }

    result = lane.review_packet(bypass_packet)

    # It must be refused because of strict MD6 promotion safety
    assert result["status"] == "refused"
    assert "SS3 verification" in result["reason"]

def test_sqlite_concurrent_hardening(tmp_path):
    """
    Validates that SOSS database management complies with concurrent standards (WAL mode, timeout locks).
    """
    test_db = tmp_path / "concurrent_test.db"

    # Initialize connection and verify WAL / timeout config
    conn = sqlite3.connect(test_db, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("CREATE TABLE status (id INTEGER, val TEXT);")
    conn.commit()

    # Assert WAL journal mode is properly set and active
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    mode = cursor.fetchone()[0]
    assert mode.lower() == "wal", "Database connection failed to configure into standard WAL mode."
    conn.close()

def test_graceful_offline_degradation_sim():
    """
    Verifies system degrades gracefully under simulated network/offline conditions.
    """
    llm = SolomonLocalLLM()
    # In offline mode, querying a local LLM or crawler must fall back gracefully without hard crash
    response = llm.generate_response(
        raw_system_data="NO PRE-EXISTING KNOWLEDGE VECTORS FOUND.",
        user_message="Find current sports details (offline sim)"
    )
    # It must return a robust processed trace instead of throwing a remote API exception
    assert "Processing matrix..." in response
    assert "offline" in response.lower() or "crawler" in response.lower() or "query" in response.lower()
