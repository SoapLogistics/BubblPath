from pydantic import BaseModel
from typing import List, Optional

class ProjectRoom(BaseModel):
    id: str
    name: str
    objective: str
    status: str
    repositories: List[str] = []
    active_branches: List[str] = []
    ai_conversations: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "id": "proj-1",
                "name": "Bezalel Foundry Foundation",
                "objective": "Build the platform.",
                "status": "active",
                "repositories": ["repo-1", "repo-2"],
                "active_branches": ["main", "feature/clipboard"],
                "ai_conversations": ["conv-1"]
            }
        }
