import time
import pytest
from core.swarm.resident_framework import global_lifecycle, global_checkpointer, global_messaging

# Ensure they are imported and registered
import services.solomon_guardian_resident
import services.solomon_jules_resident

def test_resident_long_duration_soak():
    # Give them a chance to start and checkpoint
    global_lifecycle.start_all()
    time.sleep(1.0)

    soak_duration = 3.0
    start_time = time.time()

    while time.time() - start_time < soak_duration:
        checkpoints = global_checkpointer.read_all()
        assert len(checkpoints) >= 2, f"Expected at least 2 residents in checkpointer, got {len(checkpoints)}"

        resident_ids = [c["id"] for c in checkpoints]
        assert "Guardian" in resident_ids, "Guardian missing from checkpoints"
        assert "Jules" in resident_ids, "Jules missing from checkpoints"

        for c in checkpoints:
            assert c["state"] in ["RUNNING", "INIT", "STOPPED"], f"Resident {c['id']} in bad state: {c['state']}"

        time.sleep(1.0)

    global_lifecycle.stop_all()
    time.sleep(1.0)

    checkpoints = global_checkpointer.read_all()
    for c in checkpoints:
        if c["id"] in ["Guardian", "Jules"]:
            assert c["state"] == "STOPPED", f"Resident {c['id']} did not stop correctly."

    messages = global_messaging.get_messages()
    assert len(messages) > 0, "No messages were published during soak test"
