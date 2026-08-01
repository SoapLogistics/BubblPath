import dataclasses
import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class EvidenceType(Enum):
    TASK_FAILURE = "TASK_FAILURE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    CONTRADICTION = "CONTRADICTION"
    MISSING_NODE = "MISSING_NODE"

@dataclasses.dataclass
class Capability:
    id: str
    name: str
    description: str
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Capability":
        return cls(**data)

@dataclasses.dataclass
class GapEvidence:
    id: str
    evidence_type: EvidenceType
    source_identifier: str
    timestamp: str
    context: Dict[str, Any]
    impact_score: float
    recurrence_count: int = 1

    def validate(self) -> None:
        if not self.id or not self.source_identifier:
            raise ValueError("id and source_identifier are required")
        if not isinstance(self.evidence_type, EvidenceType):
            raise ValueError(f"Invalid evidence type: {self.evidence_type}")

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d['evidence_type'] = self.evidence_type.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GapEvidence":
        data = data.copy()
        if isinstance(data.get('evidence_type'), str):
            data['evidence_type'] = EvidenceType(data['evidence_type'])
        return cls(**data)

@dataclasses.dataclass
class Prerequisite:
    capability_id: str
    is_hard_blocker: bool

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prerequisite":
        return cls(**data)

@dataclasses.dataclass
class Assessment:
    id: str
    criteria: str
    passing_threshold: float
    type: str # e.g. "PRACTICE", "EXPERIMENT", "VERIFICATION"

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assessment":
        return cls(**data)

@dataclasses.dataclass
class StudyUnit:
    id: str
    type: str # KNOWLEDGE_ACQUISITION, IMPLEMENTATION_PRACTICE, EXPERIMENT, VERIFICATION
    description: str
    resource_descriptors: List[str]
    estimated_cost: float

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudyUnit":
        return cls(**data)

@dataclasses.dataclass
class LearningObjective:
    id: str
    target_capability_id: str
    reason: str
    priority_score: float
    estimated_cost: float
    expected_artifact: str
    stop_condition: str
    prerequisites: List[Prerequisite]
    study_units: List[StudyUnit]
    assessment: Assessment
    score_components: Dict[str, float] = dataclasses.field(default_factory=dict)

    def validate(self) -> None:
        if not self.id or not self.target_capability_id:
            raise ValueError("id and target_capability_id are required")
        if self.priority_score < 0:
            raise ValueError("priority_score cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d['prerequisites'] = [p.to_dict() for p in self.prerequisites]
        d['study_units'] = [s.to_dict() for s in self.study_units]
        d['assessment'] = self.assessment.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningObjective":
        data = data.copy()
        data['prerequisites'] = [Prerequisite.from_dict(p) for p in data.get('prerequisites', [])]
        data['study_units'] = [StudyUnit.from_dict(s) for s in data.get('study_units', [])]
        data['assessment'] = Assessment.from_dict(data.get('assessment', {}))
        return cls(**data)

@dataclasses.dataclass
class CurriculumPlan:
    id: str
    objectives: List[LearningObjective]
    total_cost: float
    budget: float
    version: str = "1.0"
    status: str = "DRAFT"
    created_at: str = dataclasses.field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    cycles_detected: List[str] = dataclasses.field(default_factory=list)
    repair_proposal: Optional[str] = None

    def validate(self) -> None:
        if not self.id:
            raise ValueError("id is required")
        if self.budget < 0:
            raise ValueError("budget cannot be negative")
        if self.total_cost > self.budget:
            raise ValueError("total_cost exceeds budget")

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d['objectives'] = [o.to_dict() for o in self.objectives]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurriculumPlan":
        data = data.copy()
        data['objectives'] = [LearningObjective.from_dict(o) for o in data.get('objectives', [])]
        return cls(**data)
