from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Union, Any
from datetime import datetime, timezone
import uuid

# Registry metadata for engine compliance
route_key = "oswald_curriculum_models"
readiness_key = "oswald_curriculum_models_ready"
internal_parent = "oswald_curriculum"
retired_reason = None

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class GapEvidence(BaseModel):
    id: str = Field(default_factory=lambda: f"gap_{uuid.uuid4().hex[:8]}")
    source: str
    description: str
    timestamp: datetime = Field(default_factory=utc_now)
    confidence: float = Field(ge=0.0, le=1.0)
    importance: float = Field(ge=0.0, le=1.0)
    related_nodes: List[str] = Field(default_factory=list)

class Prerequisite(BaseModel):
    objective_id: str
    required: bool = True
    min_score: float = 0.8

class StudyUnit(BaseModel):
    id: str = Field(default_factory=lambda: f"unit_{uuid.uuid4().hex[:8]}")
    title: str
    description: str
    estimated_cost: float = Field(ge=0.0)
    unit_type: Literal['knowledge', 'practice', 'experiment', 'verification']
    resource_descriptor: Optional[str] = None
    expected_artifact: Optional[str] = None

class Assessment(BaseModel):
    method: Literal['quiz', 'code_review', 'experiment_result', 'peer_eval']
    passing_score: float = Field(ge=0.0, le=1.0)
    description: str

class LearningObjective(BaseModel):
    id: str = Field(default_factory=lambda: f"obj_{uuid.uuid4().hex[:8]}")
    title: str
    description: str
    priority_score: float = Field(default=0.0, ge=0.0)
    reasoning: str = ""
    prerequisites: List[Prerequisite] = Field(default_factory=list)
    study_units: List[StudyUnit] = Field(default_factory=list)
    assessment: Assessment
    stop_condition: str
    status: Literal['pending', 'in_progress', 'completed', 'failed', 'blocked'] = 'pending'

class CurriculumPlan(BaseModel):
    id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    version: str = "1.0.0"
    objectives: List[LearningObjective] = Field(default_factory=list)
    budget: float = Field(ge=0.0)
    consumed_budget: float = 0.0
    status: Literal['draft', 'active', 'completed', 'failed'] = 'draft'
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    seed: Optional[int] = None
    max_branching: int = 5
