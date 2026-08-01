import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class MemoryFeatures(BaseModel):
    """Features extracted from a KnowledgeCard and its context for scoring."""
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    provenance_reliability: float = Field(default=0.0, ge=0.0, le=1.0)
    corroboration_level: float = Field(default=0.0, ge=0.0, le=1.0)
    specificity: float = Field(default=0.0, ge=0.0, le=1.0)
    novelty: float = Field(default=0.0, ge=0.0, le=1.0)
    utility: float = Field(default=0.0, ge=0.0, le=1.0)
    stability: float = Field(default=0.0, ge=0.0, le=1.0)
    contradiction_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    verification_status: float = Field(default=0.0, ge=0.0, le=1.0) # 1.0 = verified, 0.5 = unverified, 0.0 = invalid

    # Contextual/historical features
    time_since_creation: float = Field(default=0.0, ge=0.0) # In days
    time_since_last_access: float = Field(default=0.0, ge=0.0) # In days
    access_count: int = Field(default=0, ge=0)
    success_retrieval_count: int = Field(default=0, ge=0)
    failure_retrieval_count: int = Field(default=0, ge=0)


class ScoringGates(BaseModel):
    """Rules that can cap or zero out the final score regardless of weights."""
    min_provenance: float = Field(default=0.0)
    min_verification: float = Field(default=0.0)
    max_contradiction: float = Field(default=1.0)


class DimensionWeights(BaseModel):
    """Weights for the different dimensions in the scoring model."""
    evidence_strength: float = Field(default=1.0)
    provenance_reliability: float = Field(default=1.0)
    corroboration_level: float = Field(default=1.0)
    specificity: float = Field(default=0.5)
    novelty: float = Field(default=0.5)
    utility: float = Field(default=1.0)
    stability: float = Field(default=1.0)
    # Contradiction is usually a penalty, so we can give it a negative weight or handle it separately.
    contradiction_penalty: float = Field(default=2.0)


class DecayPolicy(BaseModel):
    """Configuration for score decay over time."""
    enabled: bool = Field(default=True)
    half_life_days: float = Field(default=30.0, gt=0.0)
    # Different domains can decay at different rates
    domain_multipliers: Dict[str, float] = Field(default_factory=dict)


class ScoringPolicy(BaseModel):
    """A versioned policy defining how to score memories."""
    version: str = Field(..., description="Semantic version of the policy (e.g., '1.0.0')")
    weights: DimensionWeights = Field(default_factory=DimensionWeights)
    gates: ScoringGates = Field(default_factory=ScoringGates)
    decay: DecayPolicy = Field(default_factory=DecayPolicy)

    def validate_policy(self) -> None:
        """Ensure the policy is internally consistent."""
        if not self.version:
            raise ValueError("Policy must have a version.")


class DimensionScores(BaseModel):
    """Individual scores for each dimension before weighting."""
    evidence_strength: float = 0.0
    provenance_reliability: float = 0.0
    corroboration_level: float = 0.0
    specificity: float = 0.0
    novelty: float = 0.0
    utility: float = 0.0
    stability: float = 0.0
    contradiction_risk: float = 0.0
    verification_status: float = 0.0


class ScoreCard(BaseModel):
    """The result of scoring a memory, immutable once created."""
    score_id: str
    card_id: str
    policy_version: str
    final_score: float = Field(ge=0.0, le=1.0)
    dimensions: DimensionScores
    raw_features: MemoryFeatures
    explanation: str
    timestamp: str
    decayed_score: Optional[float] = None

    model_config = {"frozen": True}
