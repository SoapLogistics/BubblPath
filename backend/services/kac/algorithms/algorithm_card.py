from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class AlgorithmCard:
    algorithm_id: str
    name: str
    family: str
    domain: str
    problem_statement: str
    inputs: List[Dict[str, str]]
    outputs: List[Dict[str, str]]
    processing_steps: List[str]
    assumptions: List[Dict[str, Any]]
    complexity: Dict[str, str]
    pseudocode: str
    confidence: float
    validation_status: str
    governance_status: str
    provenance: Dict[str, Any]
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return self.__dict__
