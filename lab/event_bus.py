import queue
import threading
import logging
from typing import Callable, Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class Event:
    def __init__(self, topic: str, payload: Any, source: Optional[str] = None):
        self.topic = topic
        self.payload = payload
        self.source = source

class CognitiveEventBus:
    """
    Thread-safe, decoupled Pub/Sub Event Bus for OS v2.0.
    Optimized for high-concurrency inner-module signaling.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CognitiveEventBus, cls).__new__(cls)
                cls._instance._init()
            return cls._instance

    def _init(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue = queue.Queue()
        self._shutdown_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._dispatch_loop, daemon=True, name="EventBusDispatcher")
        self._worker_thread.start()

    def subscribe(self, topic: str, callback: Callable[[Event], None]) -> None:
        """Subscribe a callback to a specific topic."""
        with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            if callback not in self._subscribers[topic]:
                self._subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[Event], None]) -> None:
        """Remove a callback from a topic."""
        with self._lock:
            if topic in self._subscribers and callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)

    def publish(self, topic: str, payload: Any, source: Optional[str] = None) -> None:
        """Publish an event to the bus asynchronously."""
        event = Event(topic, payload, source)
        self._queue.put(event)

    def publish_sync(self, topic: str, payload: Any, source: Optional[str] = None) -> None:
        """Publish an event and execute callbacks synchronously (blocking)."""
        event = Event(topic, payload, source)
        self._execute_callbacks(event)

    def _dispatch_loop(self):
        """Background thread loop to dispatch events."""
        while not self._shutdown_event.is_set():
            try:
                # Timeout allows periodic checking of shutdown_event
                event = self._queue.get(timeout=1.0)
                self._execute_callbacks(event)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:  # noqa: BLE001
                logger.error(f"EventBus error in dispatch loop: {e}")

    def _execute_callbacks(self, event: Event):
        with self._lock:
            # Copy the list to avoid mutations during iteration
            callbacks = list(self._subscribers.get(event.topic, []))
            # Also get wildcard subscribers
            wildcard_callbacks = list(self._subscribers.get("*", []))

        all_callbacks = set(callbacks + wildcard_callbacks)

        for callback in all_callbacks:
            try:
                callback(event)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error executing callback {callback} for event {event.topic}: {e}")

    def shutdown(self):
        """Gracefully shutdown the event bus dispatcher."""
        self._shutdown_event.set()
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
