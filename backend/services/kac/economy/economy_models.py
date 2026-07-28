from dataclasses import dataclass, field
from typing import Dict, Any
import time

@dataclass
class KnowledgeValue:
    novelty: float = 0.5
    evidence: float = 0.5
    confidence: float = 0.5
    cross_domain_value: float = 0.5
    prediction_value: float = 0.5
    algorithm_value: float = 0.5
    planning_value: float = 0.5
    memory_value: float = 0.5
    compression_value: float = 0.5

    @property
    def total_score(self) -> float:
        return sum(self.__dict__.values()) / len(self.__dict__)

@dataclass
class KnowledgeYield:
    artifact_id: str
    reuse_count: int = 0
    subsystems_improved: int = 0
    predictions_improved: int = 0
    algorithms_improved: int = 0
    last_reused_at: float = field(default_factory=time.time)

    @property
    def yield_score(self) -> float:
        return (self.reuse_count * 0.4) + (self.subsystems_improved * 0.3) + (self.predictions_improved * 0.15) + (self.algorithms_improved * 0.15)
