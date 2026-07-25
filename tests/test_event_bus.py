import pytest
import time
from solomon_core.event_bus import CognitiveEventBus, Event

def test_event_bus_sync():
    bus = CognitiveEventBus()
    received_events = []

    def callback(event: Event):
        received_events.append(event.payload)

    bus.subscribe("test_topic", callback)
    bus.publish_sync("test_topic", "test_payload")

    assert "test_payload" in received_events

    bus.unsubscribe("test_topic", callback)
    bus.publish_sync("test_topic", "test_payload_2")

    assert "test_payload_2" not in received_events

def test_event_bus_async():
    bus = CognitiveEventBus()
    received_events = []

    def callback(event: Event):
        received_events.append(event.payload)

    bus.subscribe("async_topic", callback)
    bus.publish("async_topic", "async_payload")

    # Wait briefly for the worker thread to process
    time.sleep(0.1)

    assert "async_payload" in received_events
