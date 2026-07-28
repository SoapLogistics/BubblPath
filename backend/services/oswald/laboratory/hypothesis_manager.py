from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time
import uuid

@dataclass
class HypothesisCard:
    hypothesis_id: str
    problem: str
    proposed_solution: str
    supporting_evidence: List[str]
    expected_improvement: str
    subsystem: str
    confidence: float = 0.5
    status: str = "PROPOSED"
    created_at: float = field(default_factory=time.time)

@dataclass
class ExperimentRecord:
    experiment_id: str
    hypothesis_id: str
    template_type: str
    independent_variables: List[str]
    dependent_variables: List[str]
    baseline_metrics: Dict[str, float]
    experimental_metrics: Dict[str, float] = field(default_factory=dict)
    status: str = "QUEUED"
    created_at: float = field(default_factory=time.time)
