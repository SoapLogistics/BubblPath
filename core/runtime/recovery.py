import logging
import uuid
import time
from typing import Dict, Any, Callable
from .nervous_system import ZeroCopyEventBus, EventStatus

logger = logging.getLogger(__name__)

class RecoveryAction:
    RETRY = 0
    QUEUE = 1
    HUMAN_REVIEW = 2
    ROLLBACK = 3

class RetryPolicy:
    """
    Deterministic exponential backoff retry policy.
    """
    def __init__(self, max_retries: int = 3, base_delay_sec: float = 2.0):
        self.max_retries = max_retries
        self.base_delay_sec = base_delay_sec

    def should_retry(self, current_retries: int) -> bool:
        return current_retries < self.max_retries

    def get_delay(self, current_retries: int) -> float:
        return self.base_delay_sec * (2 ** current_retries)

class FailureRecoveryManager:
    """
    Manages failure recovery workflow: Retry -> Queue -> Human Review -> Rollback.
    Integrates with ZeroCopyEventBus and JobQueue.
    """
    def __init__(self, event_bus: ZeroCopyEventBus, job_queue_ref: Any):
        self.event_bus = event_bus
        self.job_queue = job_queue_ref
        self.retry_policy = RetryPolicy()

    def handle_failure(self, event_data: Dict[str, Any], ptr_index: int, error_msg: str):
        """
        Escalation logic for a failed event.
        """
        retries = event_data.get('retry_count', 0)
        category = event_data.get('category')
        priority = event_data.get('priority', 0)

        logger.warning(f"Handling failure for event ptr {ptr_index}. Retries: {retries}. Error: {error_msg}")

        if self.retry_policy.should_retry(retries):
            # 1. RETRY
            logger.info(f"Action: RETRY for event ptr {ptr_index}")
            delay = self.retry_policy.get_delay(retries)
            # Increment retry count and requeue delayed
            event_data['retry_count'] = retries + 1
            self.job_queue.submit_job(event_data, priority=priority, delay_sec=delay)
            # Mark original event as FAILED in bus (it is resubmitted to queue)
            self.event_bus.complete_event(ptr_index, EventStatus.FAILED, 0)

        else:
            # 2. QUEUE (Dead Letter Queue logic)
            # 3. HUMAN REVIEW
            logger.error(f"Action: HUMAN_REVIEW for event ptr {ptr_index} after {retries} retries.")
            self._escalate_to_governance(event_data, error_msg)
            self.event_bus.complete_event(ptr_index, EventStatus.FAILED, 0)

    def _escalate_to_governance(self, event_data: Dict[str, Any], error_msg: str):
        """Publish failure to governance for human review."""
        try:
            from .nervous_system import EventCategory
            # We publish a Governance event indicating failure review is needed
            # In a real system, payload_hash would point to the error details
            self.event_bus.publish(
                category=EventCategory.GOVERNANCE,
                priority=0, # High priority for human review
                payload_hash=hash(error_msg) % (2**63 - 1)
            )
            logger.info("Escalated failure to Governance Event Category.")
        except Exception as e:
            logger.critical(f"Failed to escalate error to governance: {e}")
