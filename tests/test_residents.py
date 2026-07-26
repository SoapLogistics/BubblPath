import os
import time
import pytest
from core.solomon_resident_framework import ResidentFramework, ResidentState
from services.solomon_guardian import SolomonGuardian
from services.solomon_jules_resident import SolomonJulesResident

TEST_SHM_FILE = 'test_residents_suite.bin'

@pytest.fixture
def resident_framework():
    # Clean up before test
    if os.path.exists(TEST_SHM_FILE):
        os.remove(TEST_SHM_FILE)

    fw = ResidentFramework(file_path=TEST_SHM_FILE)
    yield fw

    # Clean up after test
    fw.shutdown()
    if os.path.exists(TEST_SHM_FILE):
        os.remove(TEST_SHM_FILE)

def test_framework_mmap_persistence(resident_framework):
    """Verify that mmap correctly saves and loads resident state."""
    resident_framework.update_heartbeat("TestResident", 42, 1001)

    state = resident_framework.get_resident_state("TestResident")
    assert state.name == "TestResident"
    assert state.state_code == 42
    assert state.task_id == 1001
    assert state.last_heartbeat > 0

def test_guardian_lifecycle(resident_framework):
    """Verify the Guardian resident's 9-step runtime loop."""
    guardian = SolomonGuardian(resident_framework)

    # Mock sleep_interval to speed up the loop
    guardian.sleep_interval = lambda: 0.1

    guardian.start()

    # Wait for the loop to run a few times
    time.sleep(0.5)

    # Update heartbeat before sleep, so it might be 7 or 8 depending on the loop
    # Let's verify the loop ran at least to the end (state 7) and checkpointed
    state = resident_framework.get_resident_state("Guardian")

    # Verify the heartbeat was updated in the mmap file
    assert state.name == "Guardian"
    assert state.state_code >= 7

    guardian.stop()
    # Let thread finish before framework gets destroyed
    time.sleep(0.2)

def test_jules_lifecycle(resident_framework):
    """Verify the Jules resident's 9-step runtime loop."""
    jules = SolomonJulesResident(resident_framework)

    # Mock sleep_interval to speed up the loop
    jules.sleep_interval = lambda: 0.1

    jules.start()

    # Wait for the loop to run a few times
    time.sleep(0.5)

    state = resident_framework.get_resident_state("Jules")

    # Verify the heartbeat was updated in the mmap file
    assert state.name == "Jules"
    assert state.state_code >= 7

    jules.stop()
    # Let thread finish before framework gets destroyed
    time.sleep(0.2)

def test_multiple_residents(resident_framework):
    """Verify the framework can handle multiple residents simultaneously."""
    guardian = SolomonGuardian(resident_framework)
    jules = SolomonJulesResident(resident_framework)

    guardian.sleep_interval = lambda: 0.1
    jules.sleep_interval = lambda: 0.1

    guardian.start()
    jules.start()

    time.sleep(0.5)

    states = resident_framework.get_all_states()
    assert len(states) == 2

    names = [s.name for s in states]
    assert "Guardian" in names
    assert "Jules" in names

    guardian.stop()
    jules.stop()
    # Let thread finish before framework gets destroyed
    time.sleep(0.2)
