from abc import ABC, abstractmethod
from typing import List, Dict, Any

class GitAdapter(ABC):
    @abstractmethod
    def get_commits(self, branch: str) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def diff(self, base: str, head: str) -> str:
        pass
