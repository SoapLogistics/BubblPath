import time
import threading
import heapq
import logging
import collections
from typing import Dict, Any, List, Optional
from .event_bus import EventBus, Event

logger = logging.getLogger(__name__)

class ScheduledJob:
    def __init__(self, execute_at: float, event: Event, recurring_interval: Optional[float] = None, priority: int = 10, dependencies: List[str] = None):
        self.execute_at = execute_at
        self.event = event
        self.recurring_interval = recurring_interval
        self.priority = priority
        self.dependencies = dependencies or []

    def __lt__(self, other: 'ScheduledJob'):
        if self.execute_at == other.execute_at:
             return self.priority < other.priority
        return self.execute_at < other.execute_at

class RuntimeScheduler:
    """
    Schedules jobs (immediate, delayed, recurring, priority, dependency-aware).
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._queue = []
        self._lock = threading.Lock()

        # Optimize memory usage with bounded deque to avoid OOM
        self._completed_events = collections.deque(maxlen=10000)
        self._completed_events_set = set() # O(1) lookup

        self._shutdown_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._loop, daemon=True, name="RuntimeScheduler")

        # Subscribe to hear about completed dependencies
        self.event_bus.subscribe("*", self._handle_event)

    def start(self):
        self._worker_thread.start()

    def stop(self):
        self._shutdown_event.set()
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)

    def _handle_event(self, event: Event):
        if event.topic.endswith(".completed"):
             with self._lock:
                 if len(self._completed_events) == self._completed_events.maxlen:
                     oldest = self._completed_events[0]
                     if oldest in self._completed_events_set:
                         self._completed_events_set.remove(oldest)
                 self._completed_events.append(event.correlation_id)
                 self._completed_events_set.add(event.correlation_id)

    def schedule(self, job: ScheduledJob):
        with self._lock:
            heapq.heappush(self._queue, job)

    def schedule_immediate(self, event: Event, priority: int = 10, dependencies: List[str] = None):
         self.schedule(ScheduledJob(time.time(), event, priority=priority, dependencies=dependencies))

    def schedule_delayed(self, delay_seconds: float, event: Event, priority: int = 10, dependencies: List[str] = None):
         self.schedule(ScheduledJob(time.time() + delay_seconds, event, priority=priority, dependencies=dependencies))

    def schedule_recurring(self, interval_seconds: float, event: Event, priority: int = 10, dependencies: List[str] = None):
         self.schedule(ScheduledJob(time.time() + interval_seconds, event, recurring_interval=interval_seconds, priority=priority, dependencies=dependencies))

    def _loop(self):
        while not self._shutdown_event.is_set():
            now = time.time()
            to_execute = []
            to_requeue = []

            with self._lock:
                while self._queue and self._queue[0].execute_at <= now:
                    job = heapq.heappop(self._queue)

                    # Check dependencies
                    can_run = True
                    for dep in job.dependencies:
                        if dep not in self._completed_events_set:
                            can_run = False
                            break

                    if can_run:
                        to_execute.append(job)
                    else:
                        # Job needs dependencies, requeue for a bit later
                        job.execute_at = now + 1.0 # check again in 1s
                        to_requeue.append(job)

                for job in to_requeue:
                    heapq.heappush(self._queue, job)

            for job in to_execute:
                self.event_bus.publish(job.event)
                if job.recurring_interval:
                     # Create new event id to avoid duplicate prevention
                     new_event = Event(job.event.topic, job.event.source, job.event.payload, job.event.destination, correlation_id=job.event.correlation_id)
                     self.schedule(ScheduledJob(time.time() + job.recurring_interval, new_event, recurring_interval=job.recurring_interval, priority=job.priority, dependencies=job.dependencies))

            time.sleep(0.01)
