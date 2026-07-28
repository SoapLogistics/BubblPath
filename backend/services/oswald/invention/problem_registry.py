from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time
import uuid

@dataclass
class ProblemRecord:
    problem_id: str
    title: str
    description: str
    domain: str
    source: str
    severity: str = "MEDIUM"
    status: str = "OBSERVED"
    created_at: float = field(default_factory=time.time)

@dataclass
class OpportunityCard:
    opportunity_id: str
    problem_ids: List[str]
    description: str
    expected_value: str
    priority: int = 50
