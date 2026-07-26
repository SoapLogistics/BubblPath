import os
import pytest
import time
from services.solomon_validation_framework import ValidationFramework, ValidationEvidence

@pytest.fixture
def temp_log_file(tmp_path):
    log_file = tmp_path / "test_validation_evidence.bin"
    yield str(log_file)
    if log_file.exists():
        log_file.unlink()

def test_initialization(temp_log_file):
    framework = ValidationFramework(log_path=temp_log_file, max_entries=10)
    assert os.path.exists(temp_log_file)
    assert os.path.getsize(temp_log_file) == framework.file_size

def test_record_and_read_evidence(temp_log_file):
    framework = ValidationFramework(log_path=temp_log_file, max_entries=10)

    # Create test evidence
    ts = time.time()
    evidence1 = ValidationEvidence(test_id=101, status=1, execution_time_ms=12.5, memory_used_kb=1024.0, timestamp=ts)

    # Record evidence
    framework.record_evidence(evidence1)

    # Read evidence back
    results = framework.read_all_evidence()

    assert len(results) == 1
    assert results[0].test_id == 101
    assert results[0].status == 1
    assert results[0].execution_time_ms == 12.5
    assert results[0].memory_used_kb == 1024.0
    assert results[0].timestamp == ts

def test_multiple_records(temp_log_file):
    framework = ValidationFramework(log_path=temp_log_file, max_entries=10)

    # Record 3 items
    for i in range(3):
        ev = ValidationEvidence(
            test_id=200 + i,
            status=i % 2,
            execution_time_ms=10.0 + i,
            memory_used_kb=512.0 * (i + 1),
            timestamp=1000.0 + i
        )
        framework.record_evidence(ev)

    results = framework.read_all_evidence()
    assert len(results) == 3

    # Verify second item
    assert results[1].test_id == 201
    assert results[1].status == 1
    assert results[1].execution_time_ms == 11.0
    assert results[1].memory_used_kb == 1024.0
    assert results[1].timestamp == 1001.0

def test_slots_usage():
    # Verify __slots__ is being used to restrict arbitrary attribute creation
    evidence = ValidationEvidence(test_id=1, status=1, execution_time_ms=1.0, memory_used_kb=1.0, timestamp=1.0)

    with pytest.raises(AttributeError):
        evidence.arbitrary_attribute = "should fail"
