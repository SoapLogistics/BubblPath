import os
import shutil
import sqlite3
import pytest
from services.solomon_governance_approval_packet import GovernanceApprovalLane
from scripts.solomon_dx import SolomonDiagnostics

def test_governance_chain_integrity_and_tampering():
    """Verify that tampering with any slot in the governance log triggers cryptographic validation failures."""
    lane = GovernanceApprovalLane()

    # Reset log file for clean test
    if os.path.exists(lane.log_file):
        os.remove(lane.log_file)
    lane._ensure_log_exists()

    # 1. Log some verified events
    p1 = {"action": "promote_ss2", "approved_by": "Mark", "requires_approval": True, "rollback_procedure": "revert git commit"}
    p2 = {"action": "deploy_mcp", "approved_by": "Mark", "requires_approval": True, "rollback_procedure": "stop systemd service"}

    res1 = lane.review_packet(p1)
    res2 = lane.review_packet(p2)

    assert res1["status"] == "approved"
    assert res2["status"] == "approved"

    # 2. Check initial cryptographic chain is valid
    assert lane.verify_governance_chain() is True

    # 3. Tamper with the log file (e.g. overwriting bytes at the beginning of the file)
    with open(lane.log_file, "r+b") as f:
        # Tamper with first slot status
        f.seek(10)
        f.write(b"TAMPERED_STATUS_VAL")

    # 4. Assert that verification correctly detects the tampering and returns False
    assert lane.verify_governance_chain() is False

def test_governance_rollback_and_refusal_rules():
    """Verify that governance rejects SS1 promotions missing explicit rollback procedures."""
    lane = GovernanceApprovalLane()

    # Explicitly empty rollback procedure
    p_bad = {"action": "deploy_experimental_skill", "approved_by": "Mark", "requires_approval": True, "rollback_procedure": ""}
    res = lane.review_packet(p_bad)

    assert res["status"] == "refused"
    assert "Requires a safe rollback procedure" in res["reason"]

def test_operational_database_compaction_and_backups():
    """Verify that diagnostics compaction and backup creation operate correctly."""
    # Create temp database to test compaction and backups
    temp_db_path = "test_resilience_temp.db"
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

    conn = sqlite3.connect(temp_db_path)
    conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);")
    conn.execute("INSERT INTO test_table (name) VALUES ('Solomon Resilience Token');")
    conn.commit()
    conn.close()

    dx = SolomonDiagnostics(db_path=temp_db_path)

    # 1. Run database integrity and vacuum checks
    db_res = dx.run_database_checks()
    assert db_res["status"] == "PASS"
    assert db_res["integrity"].lower() == "ok"
    assert db_res["compacted"] is True

    # 2. Run backup procedure
    backup_dir = "test_backups"
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)

    backup_res = dx.run_backup_procedure(dest_dir=backup_dir)
    assert backup_res["status"] == "PASS"
    assert "backup_file" in backup_res

    # 3. Assert backup database is valid and readable
    backup_file = backup_res["backup_file"]
    conn_b = sqlite3.connect(backup_file)
    cursor = conn_b.cursor()
    cursor.execute("SELECT name FROM test_table;")
    row = cursor.fetchone()
    assert row[0] == "Solomon Resilience Token"
    conn_b.close()

    # Clean up temp artifacts
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
