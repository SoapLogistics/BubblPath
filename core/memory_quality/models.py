import datetime
import uuid
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

class QualityDimensions(BaseModel):
    """Features extracted from a memory record used for scoring."""
    evidence: float = Field(0.0, ge=0.0, le=1.0)
    provenance: float = Field(0.0, ge=0.0, le=1.0)
    corroboration: float = Field(0.0, ge=0.0, le=1.0)
    specificity: float = Field(0.0, ge=0.0, le=1.0)
    freshness: float = Field(0.0, ge=0.0, le=1.0)
    novelty: float = Field(0.0, ge=0.0, le=1.0)
    utility: float = Field(0.0, ge=0.0, le=1.0)
    stability: float = Field(0.0, ge=0.0, le=1.0)
    contradiction_risk: float = Field(0.0, ge=0.0, le=1.0)
    verification_status: str = Field("UNVALIDATED")

class ScoringPolicy(BaseModel):
    """Configuration for how dimensions are weighted and gated."""
    version: str = Field(..., description="Semantic version of the policy")
    weights: Dict[str, float] = Field(..., description="Weights for each dimension")
    domain_decay_rates: Dict[str, float] = Field(default_factory=dict, description="Decay rate multipliers by domain")
    default_decay_rate: float = Field(1.0, ge=0.0)
    gates: Dict[str, Any] = Field(default_factory=dict, description="Hard constraints that must be met")

class ScoreExplanation(BaseModel):
    """Explanation of how a score was calculated."""
    base_score: float
    gated: bool
    gate_reason: Optional[str] = None
    dimension_contributions: Dict[str, float]
    decay_penalty: float = 0.0

class MemoryQualityScore(BaseModel):
    """Immutable record of a quality score calculation."""
    score_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    record_id: str
    policy_version: str
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    final_score: float = Field(..., ge=0.0, le=1.0)
    features_snapshot: QualityDimensions
    explanation: ScoreExplanation
