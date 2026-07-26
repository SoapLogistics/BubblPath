import time
import pytest
from core.runtime.event_bus import EventBus, Event
from core.runtime.scheduler import RuntimeScheduler, ScheduledJob
from core.runtime.worker import Worker, WorkerContext
from core.runtime.runtime import SolomonRuntime

def test_event_bus_pub_sub():
    bus = EventBus()
    received = []

    def handler(event):
        received.append(event)

    bus.subscribe("test.topic", handler)
    bus.publish_sync(Event("test.topic", "test_source", {"data": 1}))

    assert len(received) == 1
    assert received[0].payload["data"] == 1

    # Test duplication prevention
    event2 = Event("test.topic", "test_source", {"data": 2})
    bus.publish_sync(event2)
    bus.publish_sync(event2)

    assert len(received) == 2 # should only be received once

    bus.shutdown()

def test_scheduler():
    bus = EventBus()
    scheduler = RuntimeScheduler(bus)
    scheduler.start()

    received = []
    def handler(event):
        received.append(event)

    bus.subscribe("test.scheduled", handler)

    scheduler.schedule_immediate(Event("test.scheduled", "source", {}))
    time.sleep(0.5) # Allow background threads to run

    assert len(received) >= 1

    scheduler.stop()
    bus.shutdown()

def test_worker_retry():
    bus = EventBus()

    class TestWorker(Worker):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attempts = 0

        def process(self, payload):
            self.attempts += 1
            if self.attempts < 2:
                raise Exception("Test failure")

    worker = TestWorker("Test", bus)
    worker.start("test.work")

    bus.publish_sync(Event("test.work", "source", {"max_retries": 2}))

    # Wait for the background thread execution of retry to finish
    time.sleep(1.5)

    assert worker.attempts == 2
    assert worker.status == "IDLE"

    bus.shutdown()

def test_full_runtime():
    runtime = SolomonRuntime()
    runtime.start()

    # Send a plan event
    runtime.event_bus.publish_sync(Event("planning.draft", "source", {}))

    status = runtime.get_status()
    assert status["status"] == "RUNNING"
    assert "PlanningWorker-1" in status["workers"]

    runtime.stop()
