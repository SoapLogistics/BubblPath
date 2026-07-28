from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time
import uuid

@dataclass
class LearningGoal:
    goal_id: str
    title: str
    description: str
    domain: str
    requested_by: str = "system"
    priority: int = 50
    status: str = "OPEN"
    current_knowledge_level: str = "UNKNOWN"
    desired_knowledge_level: str = "VALIDATED"
    success_criteria: str = ""
    created_at: float = field(default_factory=time.time)

@dataclass
class LearningObjective:
    objective_id: str
    goal_id: str
    description: str
    status: str = "PENDING"
    prerequisite_concept_ids: List[str] = field(default_factory=list)
