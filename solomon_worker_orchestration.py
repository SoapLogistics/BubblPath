import hashlib
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Task:
    def __init__(self, task_id: str, description: str, worker_type: str, dependencies: List[str] = None):
        self.task_id = task_id
        self.description = description
        self.worker_type = worker_type
        self.dependencies = dependencies or []
        self.status = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
        self.result = None

    def generate_hash(self) -> str:
        """Hash to prevent duplicated work."""
        content = f"{self.worker_type}:{self.description}"
        return hashlib.md5(content.encode()).hexdigest()

class SwarmMemory:
    """Shared memory/blackboard for swarm intelligence."""
    def __init__(self):
        self.blackboard: Dict[str, Any] = {}
        self.completed_hashes: Set[str] = set()

    def get(self, key: str) -> Any:
        return self.blackboard.get(key)

    def set(self, key: str, value: Any):
        self.blackboard[key] = value

class Worker:
    """Base worker class."""
    worker_type = "BaseWorker"
    hierarchy_level = 0

    def __init__(self, name: str, memory: SwarmMemory):
        self.name = name
        self.memory = memory

    def process(self, task: Task) -> Any:
        logger.info(f"[{self.worker_type}] {self.name} processing task: {task.description}")
        result = self._execute(task)
        logger.info(f"[{self.worker_type}] {self.name} completed task: {task.description}")
        return result

    def _execute(self, task: Task) -> Any:
        raise NotImplementedError("Subclasses must implement _execute")


# Hierarchy of Workers

class Architect(Worker):
    worker_type = "Architect"
    hierarchy_level = 10  # Highest level, designs the overall system

    def _execute(self, task: Task) -> Any:
        return f"Architecture design for: {task.description}"


class Planner(Worker):
    worker_type = "Planner"
    hierarchy_level = 9  # Breaks down architecture into plans

    def _execute(self, task: Task) -> Any:
        return f"Plan created for: {task.description}"


class Researcher(Worker):
    worker_type = "Researcher"
    hierarchy_level = 8

    def _execute(self, task: Task) -> Any:
        return f"Research results for: {task.description}"


class Security(Worker):
    worker_type = "Security"
    hierarchy_level = 7

    def _execute(self, task: Task) -> Any:
        return f"Security audit for: {task.description}"


class Optimizer(Worker):
    worker_type = "Optimizer"
    hierarchy_level = 6

    def _execute(self, task: Task) -> Any:
        return f"Optimized execution for: {task.description}"


class ToolExpert(Worker):
    worker_type = "Tool Expert"
    hierarchy_level = 5

    def _execute(self, task: Task) -> Any:
        return f"Tool selection and usage for: {task.description}"


class Builder(Worker):
    worker_type = "Builder"
    hierarchy_level = 4

    def _execute(self, task: Task) -> Any:
        return f"Built artifact for: {task.description}"


class Debugger(Worker):
    worker_type = "Debugger"
    hierarchy_level = 3

    def _execute(self, task: Task) -> Any:
        return f"Debugged artifact for: {task.description}"


class Reviewer(Worker):
    worker_type = "Reviewer"
    hierarchy_level = 2

    def _execute(self, task: Task) -> Any:
        return f"Review completed for: {task.description}"


class Documentation(Worker):
    worker_type = "Documentation"
    hierarchy_level = 1

    def _execute(self, task: Task) -> Any:
        return f"Documentation generated for: {task.description}"


class Memory(Worker):
    worker_type = "Memory"
    hierarchy_level = 0

    def _execute(self, task: Task) -> Any:
        return f"Memory stored for: {task.description}"


class SwarmOrchestrator:
    """Manages worker swarm, prevents duplicates, schedules tasks with DAG dependency resolution."""
    def __init__(self):
        self.memory = SwarmMemory()
        self.workers: Dict[str, List[Worker]] = {}
        self.tasks: Dict[str, Task] = {}
        self._initialize_workers()

    def _initialize_workers(self):
        worker_classes = [
            Architect, Planner, Researcher, Security, Optimizer, ToolExpert,
            Builder, Debugger, Reviewer, Documentation, Memory
        ]
        for cls in worker_classes:
            worker = cls(name=f"{cls.worker_type}-1", memory=self.memory)
            self.workers[cls.worker_type] = [worker]

    def add_task(self, task: Task):
        # Prevent duplicated work by checking hash against completed memory
        task_hash = task.generate_hash()
        if task_hash in self.memory.completed_hashes:
            logger.info(f"Skipping duplicate task: {task.description}")
            task.status = "COMPLETED"
            task.result = "Duplicate task result (cached)"
            self.tasks[task.task_id] = task
            return

        self.tasks[task.task_id] = task

    def execute_swarm(self):
        """Improve scheduling with DAG dependency resolution and hierarchy levels."""
        pending_tasks = set(self.tasks.keys())

        # Keep looping until all tasks are executed or a deadlock is found
        while pending_tasks:
            executable_tasks = []
            for task_id in pending_tasks:
                task = self.tasks[task_id]
                if task.status == "COMPLETED":
                    continue
                # Check if dependencies are resolved
                can_execute = True
                for dep_id in task.dependencies:
                    if dep_id in self.tasks and self.tasks[dep_id].status != "COMPLETED":
                        can_execute = False
                        break
                if can_execute:
                    executable_tasks.append(task)

            if not executable_tasks and pending_tasks:
                # Potential deadlock or circular dependency
                logger.error("Deadlock detected in swarm task execution. Remaining tasks cannot be scheduled.")
                break

            # Sort executable tasks by worker hierarchy level (highest first, meaning Architect runs before Planner if independent)
            executable_tasks.sort(key=lambda t: self._get_worker_level(t.worker_type), reverse=True)

            for task in executable_tasks:
                task.status = "IN_PROGRESS"
                worker = self._get_available_worker(task.worker_type)
                if worker:
                    result = worker.process(task)
                    task.result = result
                    task.status = "COMPLETED"
                    # Add to completed hashes to prevent future duplicates
                    self.memory.completed_hashes.add(task.generate_hash())
                    # Store result in blackboard for cooperation across swarm
                    self.memory.set(f"task_result_{task.task_id}", result)
                else:
                    logger.warning(f"No available worker for type {task.worker_type}")
                    task.status = "FAILED"

                pending_tasks.remove(task.task_id)

    def _get_worker_level(self, worker_type: str) -> int:
        if worker_type in self.workers and self.workers[worker_type]:
            return self.workers[worker_type][0].hierarchy_level
        return 0

    def _get_available_worker(self, worker_type: str) -> Optional[Worker]:
        if worker_type in self.workers and self.workers[worker_type]:
            return self.workers[worker_type][0]
        return None
