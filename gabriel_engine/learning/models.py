from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone

class LearningRecord(BaseModel):
    record_id: str = Field(..., description="Unique ID for the learning record")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Raw evidence collected")
    observations: List[str] = Field(default_factory=list, description="Derived observations")
    hypothesis: Optional[Dict[str, Any]] = Field(default=None, description="Hypothesis for testing")
    validation_status: str = Field(default="PENDING", description="PENDING, VALIDATED, REJECTED")
    confidence: float = Field(default=0.0)
    supporting_missions: List[str] = Field(default_factory=list)
    contradicting_missions: List[str] = Field(default_factory=list)
    procedure: Optional[Dict[str, Any]] = Field(default=None, description="The validated procedure rules")
    consumers: List[str] = Field(default_factory=list, description="Downstream consumers (e.g. Planner)")
    retirement_conditions: List[str] = Field(default_factory=list)
    version: str = Field(default="1.0")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProcedureCandidate(BaseModel):
    procedure_id: str = Field(..., description="Unique ID for the procedure")
    name: str = Field(..., description="Human-readable name")
    applies_when: Dict[str, Any] = Field(..., description="Conditions under which this procedure applies")
    recommended_action: List[str] = Field(..., description="List of recommended actions")
    supporting_outcomes: int = Field(default=0)
    contradicting_outcomes: int = Field(default=0)
    success_rate_before: float = Field(default=0.0)
    success_rate_after: float = Field(default=0.0)
    confidence: float = Field(default=0.0)
    status: str = Field(default="CANDIDATE", description="CANDIDATE, VALIDATED, REJECTED, RETIRED")
    last_reviewed: str = Field(..., description="Date of last review")
    evidence_ids: List[str] = Field(default_factory=list, description="List of evidence IDs")

class AgentPerformanceProfile(BaseModel):
    agent_id: str
    task_classes: List[str]
    success_rate: float
    feedback_notes: List[str]

class FailurePreventionRule(BaseModel):
    rule_id: str
    description: str
    condition: Dict[str, Any]
    preventative_action: str
    status: str = "ADVISORY"
