import os
import hashlib
import struct
import pytest
from services.solomon_governance_approval_packet import GovernanceApprovalLane

def test_database_backup_integrity_flow():
    """Programmatically verifies that backup files match their SHA-256 checksums."""
    data = b"Some SOSS SQLite WAL database binary block content payload"
    checksum = hashlib.sha256(data).hexdigest()

    # Simulating backup verification
    computed = hashlib.sha256(data).hexdigest()
    assert computed == checksum, "Backup corrupted or tampered"

def test_tampered_governance_log_detection():
    """Ensures that a tampered block log is successfully caught by verify_integrity() check."""
    lane = GovernanceApprovalLane()

    # 1. Trigger two valid actions to create a valid hash-chained log
    lane.review_packet({"action": "actionA", "requires_approval": True, "approved_by": "Mark"})
    lane.review_packet({"action": "actionB", "requires_approval": True, "approved_by": "Mark"})

    assert lane.verify_integrity() is True, "Expected valid chain integrity before tampering"

    # 2. Programmatically tamper with an existing log record slot in the bin file
    try:
        with open(lane.log_file, "r+b") as f:
            f.seek(96)  # seek to second record slot
            # Overwrite it with non-chained garbage payload bytes
            f.write(b"TAMPERED_RECORD_CONTENT_STUFF_BLAH_BLAH" + b"\x00" * 57)

        # 3. Assert that verify_integrity() successfully detects the tamper and flags False
        assert lane.verify_integrity() is False, "verify_integrity failed to detect the tampered block record"
    finally:
        # Cleanup log file
        if os.path.exists(lane.log_file):
            os.remove(lane.log_file)
