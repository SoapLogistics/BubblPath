from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class IWorkerSwarm(ABC):
    """
    Contract for multi-agent parallel execution.
    Implementations must coordinate tasks across multiple agents and synthesize consensus.
    """
    @abstractmethod
    def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

class IDataProvider(ABC):
    """
    Contract for external data retrieval tools used by agents.
    """
    @abstractmethod
    def fetch(self, query: str) -> str:
        pass

class ISandbox(ABC):
    """
    Contract for isolated code execution (Crucible).
    """
    @abstractmethod
    def execute(self, code: str, inputs: Dict[str, Any], timeout: int = 5) -> Dict[str, Any]:
        pass
