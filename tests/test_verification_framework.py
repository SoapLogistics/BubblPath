import os
import pytest
import time
from services.solomon_verification_framework import VerificationFramework, VerificationEvidence

@pytest.fixture
def verif_framework():
    # Setup
    log_file = "test_verification_log.bin"
    vf = VerificationFramework(log_file=log_file)

    yield vf

    # Teardown
    if os.path.exists(log_file):
        os.remove(log_file)

def test_evidence_recording(verif_framework):
    test_hash = hash("test_auth_module") & 0xffffffff
    evidence = VerificationEvidence(test_id_hash=test_hash, status=1, duration_ms=150, memory_kb=1024)

    # Record
    success = verif_framework.record_evidence(evidence)
    assert success is True

    # Retrieve
    retrieved = verif_framework.retrieve_evidence(test_hash)
    assert retrieved is not None
    assert retrieved.test_id_hash == test_hash
    assert retrieved.status == 1
    assert retrieved.duration_ms == 150
    assert retrieved.memory_kb == 1024

def test_evidence_not_found(verif_framework):
    retrieved = verif_framework.retrieve_evidence(999999)
    assert retrieved is None

def test_slots_efficiency():
    evidence = VerificationEvidence(test_id_hash=123, status=0, duration_ms=10, memory_kb=50)
    # Ensure __slots__ is enforced (no __dict__)
    assert not hasattr(evidence, "__dict__")
