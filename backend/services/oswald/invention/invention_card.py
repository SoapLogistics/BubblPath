from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class InventionCard:
    invention_id: str
    title: str
    summary: str
    problem_ids: List[str]
    novelty_status: str
    proposed_method: str
    expected_benefit: str
    risk_level: str
    experiment_status: str = "PENDING"
    governance_level: str = "PROTOTYPE_CANDIDATE"
    created_at: float = field(default_factory=time.time)
