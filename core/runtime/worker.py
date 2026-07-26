import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WorkerState:
    INIT = "INIT"
    RUNNING = "RUNNING"
    HALTED = "HALTED"
    FAILED = "FAILED"

class WorkerBase(ABC):
    """
    Base class for stateless, restartable, observable, and idempotent workers.
    """
    def __init__(self, name: str):
        self.name = name
        self.state = WorkerState.INIT
        self.start_time: Optional[float] = None
        self.metrics = {
            "events_processed": 0,
            "errors": 0,
            "last_event_time": None
        }

    def start(self):
        self.state = WorkerState.RUNNING
        self.start_time = time.time()
        logger.info(f"Worker {self.name} started.")

    def halt(self):
        self.state = WorkerState.HALTED
        logger.info(f"Worker {self.name} halted.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "metrics": self.metrics
        }

    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Wrapper to process an event deterministically.
        Subclasses should implement `_handle_event`.
        """
        if self.state != WorkerState.RUNNING:
            logger.warning(f"Worker {self.name} is not running, skipping event.")
            return False

        start_ms = int(time.time() * 1000)
        try:
            success = self._handle_event(event)
            self.metrics["events_processed"] += 1
            self.metrics["last_event_time"] = time.time()
            return success
        except Exception as e:
            logger.error(f"Worker {self.name} failed to process event: {e}", exc_info=True)
            self.metrics["errors"] += 1
            return False

    @abstractmethod
    def _handle_event(self, event: Dict[str, Any]) -> bool:
        """Core logic to process the event. Must be idempotent."""
        pass


class RetrievalWorker(WorkerBase):
    def __init__(self):
        super().__init__("RetrievalWorker")

    def _handle_event(self, event: Dict[str, Any]) -> bool:
        logger.info(f"RetrievalWorker processing event {event['id']}")
        return True

class PlanningWorker(WorkerBase):
    def __init__(self):
        super().__init__("PlanningWorker")

    def _handle_event(self, event: Dict[str, Any]) -> bool:
        logger.info(f"PlanningWorker processing event {event['id']}")
        return True

class LearningWorker(WorkerBase):
    def __init__(self):
        super().__init__("LearningWorker")

    def _handle_event(self, event: Dict[str, Any]) -> bool:
        logger.info(f"LearningWorker processing event {event['id']}")
        return True

class EngineeringWorker(WorkerBase):
    def __init__(self):
        super().__init__("EngineeringWorker")

    def _handle_event(self, event: Dict[str, Any]) -> bool:
        logger.info(f"EngineeringWorker processing event {event['id']}")
        return True

class BrowserWorker(WorkerBase):
    def __init__(self):
        super().__init__("BrowserWorker")

    def _handle_event(self, event: Dict[str, Any]) -> bool:
        logger.info(f"BrowserWorker processing event {event['id']}")
        return True

class ReviewWorker(WorkerBase):
    def __init__(self):
        super().__init__("ReviewWorker")

    def _handle_event(self, event: Dict[str, Any]) -> bool:
        logger.info(f"ReviewWorker processing event {event['id']}")
        return True
