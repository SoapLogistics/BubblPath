import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LearningRecord(BaseModel):
    model_config = {"frozen": True}

    id: str = Field(..., description="Unique identifier for the learning record.")
    mission_id: Optional[str] = Field(None, description="The mission during which this was learned.")
    objective: str = Field(..., description="The objective or procedure this record addresses.")
    outcome: str = Field(..., description="The outcome of the action.")
    agent: str = Field(..., description="The agent that performed the action.")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence supporting this learning.")
    contradicting_evidence: List[str] = Field(default_factory=list, description="Evidence contradicting this learning.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this learning record.")
    procedure_id: str = Field(..., description="The ID of the procedure or concept learned.")
    status: str = Field(..., description="Lifecycle state: CANDIDATE, VALIDATED, ACTIVE, REJECTED, RETIRED, DEGRADED")
    checksum: str = Field(..., description="Deduplication checksum based on content.")
