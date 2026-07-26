import os
from backend.services.joe_blueprint_facade import queue_blueprint
import scripts.scheduler
import json

def test_joe_dry_run():
    packet = queue_blueprint("some blueprint text")
    assert packet["status"] == "dry_run"
    assert "approvals" in packet

def test_scheduler_gated():
    os.environ.pop("SOLOMON_ENABLE_LOKI_SCHEDULER", None)
    log_path = "local_log/scheduler_status.log"
    if os.path.exists(log_path):
        os.remove(log_path)
    scripts.scheduler.run_scheduler()
    assert not os.path.exists(log_path)

def test_model_weights_schema():
    with open("backend/data/model_weights.json", "r") as f:
        data = json.load(f)
    assert "schema" in data
    assert "authority" in data
    assert data["state_bucket"] == "fixture"

def test_engine_registry_quantized_metadata():
    with open("solomon_api/engine_registry.json", "r") as f:
        data = json.load(f)
    assert len(data) > 0
    loki = next((e for e in data if e["engine_id"] == "soss_loki_picks"), None)
    assert loki is not None
    assert loki["runtime_tier"] == "T1_deterministic"

    joe = next((e for e in data if e["engine_id"] == "joe_blueprint_queue"), None)
    assert joe is not None
    assert joe["runtime_tier"] == "T1_deterministic_for_dry_run"
