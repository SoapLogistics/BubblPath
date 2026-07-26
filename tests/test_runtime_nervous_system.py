import os
import time
import uuid
import pytest
from core.runtime import ZeroCopyEventBus, EventCategory, EventStatus
from core.runtime import JobQueue
from core.runtime import FailureRecoveryManager, RetryPolicy

def test_zero_copy_event_bus():
    bus = ZeroCopyEventBus(filepath="test_nervous_system.bin", max_events=10)

    try:
        # Publish
        event_id = bus.publish(category=EventCategory.SYSTEM, priority=1, source_hash=123, dest_hash=456)

        # Poll
        events = bus.poll_events(limit=5)
        assert len(events) == 1
        assert events[0]['category'] == EventCategory.SYSTEM
        assert events[0]['status'] == EventStatus.PENDING # poll returns old status but updates mmap

        # Poll again (should be empty since it's PROCESSING)
        events_2 = bus.poll_events(limit=5)
        assert len(events_2) == 0

        # Complete
        bus.complete_event(ptr_index=events[0]['ptr_index'], status=EventStatus.SUCCESS, duration_ms=10)

        # Verify it doesn't get picked up again
        events_3 = bus.poll_events(limit=5)
        assert len(events_3) == 0

    finally:
        bus.close()
        if os.path.exists("test_nervous_system.bin"):
            os.remove("test_nervous_system.bin")

def test_job_queue_dag():
    queue = JobQueue()

    # Create independent job
    job1_id = queue.submit_job(event_data={"task": 1}, priority=0)

    # Create dependent job
    job2_id = queue.submit_job(event_data={"task": 2}, priority=0, depends_on=[job1_id])

    # Poll (only job1 should be ready)
    ready = queue.poll_ready_jobs()
    assert len(ready) == 1
    assert ready[0].job_id == job1_id

    # Complete job1
    queue.complete_job(job1_id, success=True)

    # Poll (now job2 should be ready)
    ready2 = queue.poll_ready_jobs()
    assert len(ready2) == 1
    assert ready2[0].job_id == job2_id

def test_failure_recovery():
    queue = JobQueue()
    bus = ZeroCopyEventBus(filepath="test_recovery_bus.bin", max_events=10)

    try:
        manager = FailureRecoveryManager(bus, queue)
        manager.retry_policy.base_delay_sec = 0.1 # fast retry for test

        event_data = {
            'category': EventCategory.MEMORY,
            'priority': 0,
            'retry_count': 0
        }

        # Fail it once (should retry)
        manager.handle_failure(event_data, ptr_index=0, error_msg="Test fail")
        assert len(queue.delayed_queue) == 1

        # Wait for delay
        time.sleep(0.15)
        ready = queue.poll_ready_jobs()
        assert len(ready) == 1
        assert ready[0].event_data['retry_count'] == 1

    finally:
        bus.close()
        if os.path.exists("test_recovery_bus.bin"):
            os.remove("test_recovery_bus.bin")
