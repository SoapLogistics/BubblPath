import threading
import time
import logging
from typing import Callable, List
from solomon_core.event_bus import CognitiveEventBus

logger = logging.getLogger(__name__)

class ScheduledTask:
    def __init__(self, name: str, interval_seconds: int, action: Callable):
        self.name = name
        self.interval = interval_seconds
        self.action = action
        self.last_run = time.time()

class SystemScheduler:
    """
    Manages recurring Wake/Sleep background loops for SPLE.
    Publishes events to the EventBus to trigger subsystem actions.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, bus: CognitiveEventBus = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SystemScheduler, cls).__new__(cls)
                cls._instance._init(bus)
            return cls._instance

    def _init(self, bus: CognitiveEventBus):
        self.bus = bus
        self.tasks: List[ScheduledTask] = []
        self._shutdown_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._tick_loop, daemon=True, name="SystemSchedulerTick")

        # Default internal loops based on SPLE blueprint
        self.register_task("light_consolidation", 60, lambda: self.bus.publish("sple.consolidation.light", {}))
        self.register_task("curiosity_pulse", 120, lambda: self.bus.publish("sple.curiosity.pulse", {}))

    def start(self):
        if not self._worker_thread.is_alive():
            self._worker_thread.start()
            logger.info("SystemScheduler started.")

    def register_task(self, name: str, interval_seconds: int, action: Callable):
        self.tasks.append(ScheduledTask(name, interval_seconds, action))

    def _tick_loop(self):
        while not self._shutdown_event.is_set():
            now = time.time()
            for task in self.tasks:
                if now - task.last_run >= task.interval:
                    try:
                        task.action()
                    except Exception as e:
                        logger.error(f"Error executing scheduled task '{task.name}': {e}")
                    finally:
                        task.last_run = now
            # Sleep briefly to prevent high CPU usage
            time.sleep(1.0)

    def shutdown(self):
        self._shutdown_event.set()
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
