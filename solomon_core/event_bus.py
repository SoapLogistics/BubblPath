import threading
import logging
from typing import Any, Dict, Callable, List
from .interfaces import IEventBus

logger = logging.getLogger("CognitiveEventBus")

class CognitiveEventBus(IEventBus):
    """
    In-memory Pub/Sub Event Bus for Project Solomon.
    Decouples subsystems (Memory, SPLE, Loki) and prevents circular dependencies.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CognitiveEventBus, cls).__new__(cls)
                cls._instance._subscribers = {}
        return cls._instance

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        """Publishes an event payload to all registered callbacks for the given topic."""
        logger.info(f"Publishing event to topic: {topic}")
        if topic in self._subscribers:
            for callback in self._subscribers[topic]:
                try:
                    # In a true high-throughput system, this might dispatch to a ThreadPoolExecutor
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error in event subscriber for topic {topic}: {e}")

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Registers a callback function to a specific topic string."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        if callback not in self._subscribers[topic]:
            self._subscribers[topic].append(callback)
            logger.debug(f"Registered subscriber for topic: {topic}")
