import logging
from typing import Dict, Any, List
from .event_bus import EventBus
from .worker import RetrievalWorker, PlanningWorker, LearningWorker, EngineeringWorker, BrowserWorker, ReviewWorker, Worker
from .scheduler import RuntimeScheduler

logger = logging.getLogger(__name__)

class SolomonRuntime:
    """
    The canonical runtime nervous system for Solomon.
    """
    def __init__(self):
        self.event_bus = EventBus()
        self.scheduler = RuntimeScheduler(self.event_bus)
        self.workers: Dict[str, Worker] = {}

    def start(self):
        logger.info("Starting Solomon Runtime...")
        self.scheduler.start()

        # Initialize standard workers
        self._register_worker(RetrievalWorker("RetrievalWorker-1", self.event_bus), "memory.retrieve")
        self._register_worker(PlanningWorker("PlanningWorker-1", self.event_bus), "planning.draft")
        self._register_worker(LearningWorker("LearningWorker-1", self.event_bus), "learning.process")
        self._register_worker(EngineeringWorker("EngineeringWorker-1", self.event_bus), "engineering.task")
        self._register_worker(BrowserWorker("BrowserWorker-1", self.event_bus), "browser.context")
        self._register_worker(ReviewWorker("ReviewWorker-1", self.event_bus), "governance.review")

        # System event listener
        self.event_bus.subscribe("system.failure", self._handle_system_failure)
        logger.info("Solomon Runtime started successfully.")

    def stop(self):
        logger.info("Stopping Solomon Runtime...")
        for worker in self.workers.values():
            worker.stop()
        self.scheduler.stop()
        self.event_bus.shutdown()
        logger.info("Solomon Runtime stopped.")

    def _register_worker(self, worker: Worker, topic: str):
        self.workers[worker.name] = worker
        worker.start(topic)

    def _handle_system_failure(self, event):
        logger.error(f"RUNTIME ALERT: Handling system failure: {event.payload}")
        # Failure recovery logic (retry, queue, human review) happens here

    def get_status(self):
        return {
            "status": "RUNNING",
            "workers": {name: w.status for name, w in self.workers.items()},
            "event_bus_queue_size": self.event_bus._queue.qsize(),
            "scheduler_queue_size": len(self.scheduler._queue)
        }
