import time
import uuid
import heapq
import threading
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DAGNode:
    """Represents a job in a directed acyclic graph."""
    def __init__(self, job_id: uuid.UUID, event_data: Dict[str, Any], priority: int = 0):
        self.job_id = job_id
        self.event_data = event_data
        self.priority = priority
        self.dependencies: List[uuid.UUID] = []
        self.status = "PENDING" # PENDING, READY, PROCESSING, SUCCESS, FAILED

    def __lt__(self, other):
        return self.priority < other.priority

class JobQueue:
    """
    Advanced Job Queue for Solomon Runtime.
    Supports: Immediate jobs, Delayed jobs, Priority queues, and DAG dependencies.
    """
    def __init__(self):
        self._lock = threading.RLock()

        # Priority Queue for ready jobs: (priority, timestamp, job_id)
        self.ready_queue = []

        # Delayed Queue: (execution_time, priority, job_id)
        self.delayed_queue = []

        # Job tracking
        self.jobs: Dict[uuid.UUID, DAGNode] = {}

        # Reverse dependency map: job_id -> list of jobs that depend on it
        self.dependents: Dict[uuid.UUID, List[uuid.UUID]] = {}

    def submit_job(self, event_data: Dict[str, Any], priority: int = 0,
                   delay_sec: float = 0, depends_on: Optional[List[uuid.UUID]] = None) -> uuid.UUID:
        with self._lock:
            job_id = uuid.uuid4()
            node = DAGNode(job_id, event_data, priority)

            if depends_on:
                node.dependencies = depends_on.copy()
                for dep_id in depends_on:
                    if dep_id not in self.dependents:
                        self.dependents[dep_id] = []
                    self.dependents[dep_id].append(job_id)

            self.jobs[job_id] = node

            # Decide where to place the job
            if delay_sec > 0:
                execute_at = time.time() + delay_sec
                heapq.heappush(self.delayed_queue, (execute_at, priority, job_id))
            elif not node.dependencies:
                node.status = "READY"
                heapq.heappush(self.ready_queue, (priority, time.time(), job_id))

            return job_id

    def poll_ready_jobs(self) -> List[DAGNode]:
        """Returns ready jobs, moving delayed jobs to ready if time is up."""
        ready_jobs = []
        now = time.time()

        with self._lock:
            # Process delayed queue
            while self.delayed_queue and self.delayed_queue[0][0] <= now:
                execute_at, priority, job_id = heapq.heappop(self.delayed_queue)
                if job_id in self.jobs:
                    node = self.jobs[job_id]
                    if not node.dependencies: # Re-check dependencies
                        node.status = "READY"
                        heapq.heappush(self.ready_queue, (priority, now, job_id))

            # Pull ready jobs
            while self.ready_queue:
                priority, ts, job_id = heapq.heappop(self.ready_queue)
                if job_id in self.jobs and self.jobs[job_id].status == "READY":
                    node = self.jobs[job_id]
                    node.status = "PROCESSING"
                    ready_jobs.append(node)

        return ready_jobs

    def complete_job(self, job_id: uuid.UUID, success: bool):
        """Mark a job complete and resolve dependencies."""
        with self._lock:
            if job_id not in self.jobs:
                return

            node = self.jobs[job_id]
            node.status = "SUCCESS" if success else "FAILED"

            if success and job_id in self.dependents:
                for dep_id in self.dependents[job_id]:
                    if dep_id in self.jobs:
                        dep_node = self.jobs[dep_id]
                        if job_id in dep_node.dependencies:
                            dep_node.dependencies.remove(job_id)
                            # If all dependencies met, move to ready
                            if not dep_node.dependencies:
                                dep_node.status = "READY"
                                heapq.heappush(self.ready_queue, (dep_node.priority, time.time(), dep_id))

            # Cleanup
            if job_id in self.dependents:
                del self.dependents[job_id]
            del self.jobs[job_id]
