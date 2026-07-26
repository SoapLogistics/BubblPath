import os
import pytest
from lab.solomon_q_engine import SolomonQEngine, QStore

@pytest.fixture
def test_q_engine():
    # Use a separate test store
    store_path = "test_q_store.bin"
    if os.path.exists(store_path):
        os.remove(store_path)
    engine = SolomonQEngine()
    engine.store = QStore(filepath=store_path)
    yield engine
    # Cleanup
    if engine.store.file_obj:
        engine.store.file_obj.close()
    if os.path.exists(store_path):
        os.remove(store_path)

def test_q_store_initialization(test_q_engine):
    assert test_q_engine.store.tail_index == 0
    assert test_q_engine.store.max_records == 10000

def test_q_engine_intake(test_q_engine):
    request_data = {"objective": "fix bug in tests", "owner_family": "jules"}
    result = test_q_engine.intake(request_data)

    assert result["status"] == "intake_success"
    assert result["index"] == 0
    assert result["risk_level"] == "LOW"
    assert test_q_engine.store.tail_index == 1

def test_q_engine_high_risk_classification(test_q_engine):
    request_data = {"objective": "deploy to SS1 production", "owner_family": "jules"}
    result = test_q_engine.intake(request_data)

    assert result["status"] == "intake_success"
    assert result["risk_level"] == "HIGH"
    assert result["next_safe_step"] == "dry_run"

def test_q_engine_memory_recall(test_q_engine):
    # Add a verified packet
    test_q_engine.intake({"objective": "fix a critical bug", "owner_family": "jules"})
    test_q_engine.loop() # verify it

    # Second packet should recall the first due to "bug" keyword
    result = test_q_engine.intake({"objective": "fix another bug", "owner_family": "jules"})

    assert result["recalled_count"] == 1

def test_q_engine_loop_verification(test_q_engine):
    test_q_engine.intake({"objective": "fix bug", "owner_family": "jules"})

    # Loop should pick it up and verify
    result = test_q_engine.loop()

    assert result["status"] == "loop_executed"
    assert result["new_state"] == "VERIFIED"
    assert result["activation_status"] == "ACTIVATED_SUPERVISED"

def test_q_engine_loop_refusal(test_q_engine):
    test_q_engine.intake({"objective": "mutate production", "owner_family": "jules"})

    # Loop should pick it up and refuse due to high risk
    result = test_q_engine.loop()

    assert result["status"] == "loop_executed"
    assert result["new_state"] == "REFUSED"
    assert "reverting to safe gate" in result["outcome"].lower()

def test_q_engine_no_pending(test_q_engine):
    result = test_q_engine.loop()
    assert result["status"] == "idle"
