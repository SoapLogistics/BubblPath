from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class IEventBus(ABC):
    """
    Unified Cognitive Event Bus for Project Solomon.
    """
    @abstractmethod
    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def subscribe(self, topic: str, callback: callable) -> None:
        pass


class IWorkerSwarm(ABC):
    """
    Standardized interface for LLM worker swarms (OpenAI, Local Quantized, Clean-Room).
    """
    @abstractmethod
    def execute_task(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass


class IDataProvider(ABC):
    """
    Standardized abstraction for fetching data (e.g., Kalshi, Sports, Finance).
    """
    @abstractmethod
    def fetch_data(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def stream_data(self, callback: callable) -> None:
        pass
