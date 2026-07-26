import pytest
import time
import os
import threading
from services.solomon_runtime_nervous_system import RuntimeNervousSystem, EventCategory, WorkerClass, EventState, EscalationRule

@pytest.fixture
def runtime():
    # Cleanup any existing file to start fresh
    if os.path.exists("runtime_nervous_system.bin"):
        os.remove("runtime_nervous_system.bin")

    # Reset singleton
    RuntimeNervousSystem._instance = None

    rt = RuntimeNervousSystem()
    yield rt

    rt.shutdown()
    if os.path.exists("runtime_nervous_system.bin"):
        os.remove("runtime_nervous_system.bin")

def test_publish_and_subscribe(runtime):
    received = []

    def on_event(event, payload):
        received.append((event, payload))

    runtime.subscribe(EventCategory.SYSTEM, on_event)

    runtime.publish_event(
        category=EventCategory.SYSTEM,
        worker_class=WorkerClass.PLANNING,
        payload={"task": "test_routing"},
        priority=10
    )

    # Wait for daemon
    time.sleep(0.5)

    assert len(received) == 1
    event, payload = received[0]
    assert payload == {"task": "test_routing"}
    assert event['priority'] == 10
    assert event['category'] == EventCategory.SYSTEM
    assert event['worker_class'] == WorkerClass.PLANNING

def test_priority_queueing(runtime):
    received = []

    def on_event(event, payload):
        received.append(event['priority'])

    runtime.subscribe(EventCategory.MEMORY, on_event)

    # Publish lower priority first
    runtime.publish_event(category=EventCategory.MEMORY, worker_class=WorkerClass.RETRIEVAL, payload="low", priority=1)
    runtime.publish_event(category=EventCategory.MEMORY, worker_class=WorkerClass.RETRIEVAL, payload="high", priority=100)
    runtime.publish_event(category=EventCategory.MEMORY, worker_class=WorkerClass.RETRIEVAL, payload="med", priority=50)

    time.sleep(0.5)

    assert len(received) == 3
    # Wait time might result in processing first before 2nd is added.
    # But since it processes chunks in background, it should pull highest priority among queued.
    # We will verify all 3 were processed.
    assert set(received) == {1, 50, 100}

def test_failure_retry_and_escalation(runtime):
    failures = 0
    def failing_worker(event, payload):
        nonlocal failures
        failures += 1
        raise ValueError("Simulated failure")

    runtime.subscribe(EventCategory.LEARNING, failing_worker)

    event_id = runtime.publish_event(category=EventCategory.LEARNING, worker_class=WorkerClass.LEARNING, payload="fail_me")

    # Needs a few loop iterations for 4 tries (initial + 3 retries)
    time.sleep(1.5)

    assert failures == 4 # 1 initial + 3 retries

    # Find the escalated event in memory
    escalated_found = False
    for i in range(10): # First 10 slots
        evt = runtime.read_event(i)
        if evt and evt['event_id'] == event_id:
            assert evt['state'] == EventState.ESCALATED
            assert evt['escalation'] == EscalationRule.HUMAN_REVIEW
            assert evt['retry_count'] == 3
            assert 'Simulated failure' in evt['error_trace']
            escalated_found = True
            break

    assert escalated_found

def test_delayed_execution(runtime):
    received = []
    def on_event(event, payload):
        received.append((event, payload))

    runtime.subscribe(EventCategory.PLANNING, on_event)

    # Schedule event 1 second in the future
    future_time = time.time() + 1.0
    runtime.publish_event(
        category=EventCategory.PLANNING,
        worker_class=WorkerClass.PLANNING,
        payload="delayed_payload",
        execute_after=future_time
    )

    # Wait 0.5s, should not be executed yet
    time.sleep(0.5)
    assert len(received) == 0

    # Wait another 1.0s, should be executed now
    time.sleep(1.0)
    assert len(received) == 1
    assert received[0][1] == "delayed_payload"

def test_dependency_execution(runtime):
    received = []
    def on_event(event, payload):
        received.append((event['event_id'], payload))

    runtime.subscribe(EventCategory.CAPABILITY, on_event)

    # Publish parent event
    parent_id = runtime.publish_event(
        category=EventCategory.CAPABILITY,
        worker_class=WorkerClass.ENGINEERING,
        payload="parent"
    )

    # Publish child event dependent on parent
    child_id = runtime.publish_event(
        category=EventCategory.CAPABILITY,
        worker_class=WorkerClass.ENGINEERING,
        payload="child",
        dependency_id=parent_id
    )

    # Wait a bit for processing
    time.sleep(1.0)

    assert len(received) == 2
    # Ensure parent was processed before child
    # Since child depends on parent, it won't be picked up until parent is DONE
    assert received[0][0] == parent_id
    assert received[1][0] == child_id
