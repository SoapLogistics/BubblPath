import uuid
import time
import queue
import threading
import logging
from typing import Dict, Any, Callable, List, Optional
from collections import defaultdict, deque
import collections

logger = logging.getLogger(__name__)

class Event:
    """Canonical Event for Solomon Event Bus."""
    def __init__(self, topic: str, source: str, payload: Dict[str, Any], destination: Optional[str] = None, correlation_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.source = source
        self.payload = payload
        self.destination = destination
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = time.time()
        self.status = "CREATED"
        self.duration = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "source": self.source,
            "destination": self.destination,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "duration": self.duration
        }

class EventBus:
    """
    Decoupled Pub/Sub Event Bus for OS v2.0.
    Standardizes internal event messaging.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._queue = queue.Queue()
        self._shutdown_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._dispatch_loop, daemon=True, name="EventBusDispatcher")

        # Optimize memory usage with Bounded Deques for processed events to avoid OOM
        self._processed_events = collections.deque(maxlen=10000)
        self._processed_events_set = set() # For O(1) lookup

        # Bounded log
        self.event_log = deque(maxlen=1000)

        self._worker_thread.start()

    def subscribe(self, topic: str, callback: Callable[[Event], None]) -> None:
        """Subscribe a callback to a specific topic."""
        with self._lock:
            if callback not in self._subscribers[topic]:
                self._subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[Event], None]) -> None:
        """Remove a callback from a topic."""
        with self._lock:
            if callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)

    def publish(self, event: Event) -> None:
        """Publish an event to the bus asynchronously."""
        with self._lock:
            if event.id in self._processed_events_set:
                logger.warning(f"Duplicate event prevented: {event.id}")
                return

            # Maintain bounds on the set
            if len(self._processed_events) == self._processed_events.maxlen:
                oldest_id = self._processed_events[0]
                if oldest_id in self._processed_events_set:
                    self._processed_events_set.remove(oldest_id)

            self._processed_events.append(event.id)
            self._processed_events_set.add(event.id)
            self._queue.put(event)

    def publish_sync(self, event: Event) -> None:
        """Publish an event and execute callbacks synchronously (blocking)."""
        with self._lock:
             if event.id in self._processed_events_set:
                logger.warning(f"Duplicate event prevented: {event.id}")
                return

             if len(self._processed_events) == self._processed_events.maxlen:
                oldest_id = self._processed_events[0]
                if oldest_id in self._processed_events_set:
                    self._processed_events_set.remove(oldest_id)

             self._processed_events.append(event.id)
             self._processed_events_set.add(event.id)
        self._execute_callbacks(event)

    def _dispatch_loop(self):
        """Background thread loop to dispatch events."""
        while not self._shutdown_event.is_set():
            try:
                event = self._queue.get(timeout=1.0)
                self._execute_callbacks(event)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"EventBus error in dispatch loop: {e}")

    def _execute_callbacks(self, event: Event):
        start_time = time.time()
        event.status = "DISPATCHING"

        with self._lock:
            callbacks = list(self._subscribers.get(event.topic, []))
            wildcard_callbacks = list(self._subscribers.get("*", []))

        all_callbacks = set(callbacks + wildcard_callbacks)

        if not all_callbacks:
            logger.debug(f"No subscribers for event: {event.topic}")
            event.status = "NO_SUBSCRIBERS"

        success_count = 0
        for callback in all_callbacks:
            try:
                callback(event)
                success_count += 1
            except Exception as e:
                logger.error(f"Error executing callback {callback} for event {event.topic}: {e}")

        event.duration = time.time() - start_time
        if success_count > 0:
            event.status = "PROCESSED"

        # Log observability
        self._log_event(event)

    def _log_event(self, event: Event):
        with self._lock:
            self.event_log.append(event.to_dict())

    def shutdown(self):
        """Gracefully shutdown the event bus dispatcher."""
        self._shutdown_event.set()
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)

    def get_logs(self):
        with self._lock:
            return list(self.event_log)
