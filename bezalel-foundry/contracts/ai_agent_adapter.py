from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIAgentAdapter(ABC):
    @abstractmethod
    async def chat(self, messages: List[Dict[str, Any]]) -> str:
        pass

    @abstractmethod
    async def review_code(self, code: str) -> str:
        pass
