import os
import pytest
import tempfile
import uuid
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.autonomous_scheduler import AutonomousScheduler
from lab.event_bus import CognitiveEventBus

def test_database_task_queue():
    """
    Validates that DatabaseManager correctly initializes persistent_tasks
    and manages claims, completions, and priority-based orderings.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_soss.db")
        db = DatabaseManager(db_path)

        task_id_1 = "task_low"
        task_id_2 = "task_high"

        # 1. Add tasks with different priorities
        db.add_task(task_id_1, "general", {"complexity": 1, "urgency_multiplier": 1.0}, priority=1)
        db.add_task(task_id_2, "self_refactoring_triggered", {"complexity": 2, "urgency_multiplier": 2.0}, priority=5)

        # 2. Claim first task (should be task_high due to higher priority)
        claimed_first = db.claim_task("worker_alpha")
        assert claimed_first is not None
        assert claimed_first["task_id"] == task_id_2
        assert claimed_first["status"] == "ACTIVE"

        # 3. Claim second task (should be task_low)
        claimed_second = db.claim_task("worker_alpha")
        assert claimed_second is not None
        assert claimed_second["task_id"] == task_id_1

        # 4. Attempt to claim a third task (should be None)
        claimed_none = db.claim_task("worker_alpha")
        assert claimed_none is None

        # 5. Complete task
        success = db.complete_task(task_id_2, "worker_alpha", "COMPLETED", "Self-refactored 2 modules.")
        assert success is True

        task_check = db.get_task(task_id_2)
        assert task_check["status"] == "COMPLETED"


def test_autonomous_scheduler_event_integration():
    """
    Validates that AutonomousScheduler links pub/sub events to the
    persistent queue and runs iterations using expected utility.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_soss_sched.db")
        scheduler = AutonomousScheduler(db_path=db_path)

        # Reset the task queue inside the scheduler DB connection
        scheduler.db = DatabaseManager(db_path)

        # 1. Publish a 'task_added' event
        event_bus = CognitiveEventBus()
        task_payload = {
            "task_id": "event_task_01",
            "topic": "evaluation_triggered",
            "priority": 10,
            "complexity": 1.5,
            "urgency_multiplier": 1.2
        }
        event_bus.publish("task_added", task_payload, source="test_suite")

        # Give some time for the async background bus to process if needed,
        # or call publish_sync to force immediate callbacks.
        event_bus.publish_sync("task_added", task_payload, source="test_suite")

        # 2. Run scheduler iteration
        executed_task = scheduler.run_one_iteration()
        assert executed_task is not None
        assert executed_task["task_id"] == "event_task_01"
        assert executed_task["topic"] == "evaluation_triggered"

        # Check database execution log
        task_final = scheduler.db.get_task("event_task_01")
        assert task_final["status"] == "COMPLETED"
