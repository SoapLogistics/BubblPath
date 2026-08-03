import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Observation(BaseModel):
    id: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    event_type: str
    details: Dict[str, Any]

class Evidence(BaseModel):
    id: str
    source_id: str
    content: str
    confidence: float

class Hypothesis(BaseModel):
    id: str
    description: str
    evidence_ids: List[str]

class Validation(BaseModel):
    id: str
    hypothesis_id: str
    result: str
    metrics: Dict[str, Any]

class ProcedureCandidate(BaseModel):
    id: str
    name: str
    description: str
    learning_record_id: str

class AgentProfile(BaseModel):
    id: str
    name: str
    capabilities: List[str] = []

class LearningRecord(BaseModel):
    id: str
    observations: List[Observation] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    validations: List[Validation] = Field(default_factory=list)
    confidence: float = 0.0
