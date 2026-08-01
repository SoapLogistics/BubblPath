from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import datetime

class ScoringPolicy(BaseModel):
    version: str = "1.0.0"
    weights: Dict[str, float] = Field(default_factory=lambda: {
        "evidence": 0.15,
        "provenance": 0.15, # Increased to reach 1.0 total
        "corroboration": 0.15, # Increased to reach 1.0 total
        "specificity": 0.10,
        "novelty": 0.10,
        "utility": 0.10,
        "stability": 0.05,
        "contradiction_risk": -0.10,
        "verification_status": 0.10,
        "freshness": 0.10
    })
    gates: Dict[str, float] = Field(default_factory=lambda: {
        "provenance": 0.2, # if provenance score < 0.2, max score is capped
        "verification_status": 0.1
    })
    decay_params: Dict[str, float] = Field(default_factory=lambda: {
        "default_half_life_days": 365.0,
        "fast_decay_half_life_days": 30.0
    })

class MemoryFeatures(BaseModel):
    # Base extracted features 0.0 to 1.0 (or appropriate scales)
    evidence_strength: float = 0.0
    provenance_reliability: float = 0.0
    corroboration_count: int = 0
    specificity_score: float = 0.0
    freshness_days: float = 0.0
    novelty_score: float = 0.0
    utility_retrieval_count: int = 0
    stability_score: float = 0.0
    contradiction_risk: float = 0.0
    verification_status: float = 0.0
    domain: str = "default"

class QualityScore(BaseModel):
    score_id: str
    card_id: str
    policy_version: str
    final_score: float
    components: Dict[str, float]
    gated_by: Optional[str] = None
    reason_codes: List[str]
    computed_at: str
    feature_snapshot: MemoryFeatures
