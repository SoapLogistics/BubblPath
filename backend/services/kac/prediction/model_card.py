from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class PredictiveModelCard:
    model_id: str
    name: str
    target: str
    inputs: List[str]
    conditions: List[str]
    horizon: str
    model_form: str
    causal_classification: str
    baseline: str
    accuracy_history: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.5
    status: str = "DISCOVERED"
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return self.__dict__
