import uuid
import time
import logging
import traceback
import threading
from typing import Dict, Any, Optional, Callable
from .event_bus import EventBus, Event

logger = logging.getLogger(__name__)

class WorkerContext:
    def __init__(self, event: Event):
        self.event = event
        self.retry_count = 0

class Worker:
    """
    Stateless, Restartable, Observable, Idempotent worker base class.
    """
    def __init__(self, name: str, event_bus: EventBus):
        self.id = str(uuid.uuid4())
        self.name = name
        self.event_bus = event_bus
        self.status = "IDLE"
        self.topic = None

    def start(self, topic: str):
        self.topic = topic
        self.event_bus.subscribe(topic, self._handle_event)
        self.status = "RUNNING"
        logger.info(f"Worker {self.name} started listening to {topic}")

    def stop(self):
        if self.topic:
            self.event_bus.unsubscribe(self.topic, self._handle_event)
        self.status = "STOPPED"
        logger.info(f"Worker {self.name} stopped.")

    def _handle_event(self, event: Event):
        # We spawn a thread to prevent blocking the main EventBus dispatcher
        context = WorkerContext(event)
        t = threading.Thread(target=self._execute_with_retry, args=(context,), daemon=True)
        t.start()
        # Note: If testing requires synchronous execution, we might need a sync mode,
        # but for production this offloads the EventBus dispatcher loop.

    def _execute_with_retry(self, context: WorkerContext):
        max_retries = context.event.payload.get("max_retries", 3)

        while context.retry_count <= max_retries:
            try:
                self.status = "PROCESSING"
                self.process(context.event.payload)
                self.status = "IDLE"

                # Publish completion event
                self.event_bus.publish(Event(
                    topic=f"{self.topic}.completed",
                    source=self.name,
                    payload={"result": "success"},
                    correlation_id=context.event.correlation_id
                ))
                return
            except Exception as e:
                context.retry_count += 1
                failure_reason = str(e)
                stack_trace = traceback.format_exc()

                logger.warning(f"Worker {self.name} failed (attempt {context.retry_count}/{max_retries}): {failure_reason}")

                if context.retry_count > max_retries:
                    self.status = "ERROR"
                    self._escalate_failure(context, failure_reason, stack_trace)
                    return
                time.sleep(1) # simple backoff

    def _escalate_failure(self, context: WorkerContext, reason: str, stack_trace: str):
         failure_event = Event(
            topic="system.failure",
            source=self.name,
            payload={
                "failure_reason": reason,
                "retry_count": context.retry_count,
                "stack_trace": stack_trace,
                "original_event": context.event.to_dict(),
                "recovery_recommendation": "Human review required" if context.retry_count > 3 else "Queue for later"
            },
            correlation_id=context.event.correlation_id
         )
         self.event_bus.publish(failure_event)

    def process(self, payload: Dict[str, Any]):
        """Override this method to implement worker logic."""
        raise NotImplementedError()

# Worker Classes
class RetrievalWorker(Worker):
    def process(self, payload: Dict[str, Any]):
        logger.info(f"RetrievalWorker processing: {payload}")

class PlanningWorker(Worker):
    def process(self, payload: Dict[str, Any]):
        logger.info(f"PlanningWorker processing: {payload}")

class LearningWorker(Worker):
     def process(self, payload: Dict[str, Any]):
        logger.info(f"LearningWorker processing: {payload}")

class EngineeringWorker(Worker):
     def process(self, payload: Dict[str, Any]):
        logger.info(f"EngineeringWorker processing: {payload}")

class BrowserWorker(Worker):
     def process(self, payload: Dict[str, Any]):
        logger.info(f"BrowserWorker processing: {payload}")

class ReviewWorker(Worker):
     def process(self, payload: Dict[str, Any]):
        logger.info(f"ReviewWorker processing: {payload}")
