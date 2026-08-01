import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator, constr

class Hypothesis(BaseModel):
    model_config = {"frozen": True}

    id: str = Field(..., description="Unique identifier for the hypothesis")
    version: str = Field("1.0", description="Schema version")
    scope: str = Field(..., min_length=1, description="Scope of the hypothesis")
    assumptions: List[str] = Field(default_factory=list, description="List of assumptions")
    predicted_direction: str = Field(..., min_length=1, description="Predicted direction (e.g., increase, decrease, neutral)")
    predicted_magnitude: str = Field(..., min_length=1, description="Predicted magnitude or effect size")
    falsification_conditions: str = Field(..., min_length=1, description="Explicit conditions under which this is false")
    linked_evidence_ids: List[str] = Field(default_factory=list, description="IDs of cards acting as evidence")
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

class ExperimentDesign(BaseModel):
    model_config = {"frozen": True}

    id: str = Field(..., description="Unique identifier for the experiment design")
    hypothesis_id: str = Field(..., description="Hypothesis this experiment tests")
    version: str = Field("1.0", description="Schema version")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Variables manipulated or measured")
    controls: List[str] = Field(..., description="List of controlled variables. Must not be empty if controls are conceptually required.")
    metrics: List[str] = Field(..., min_length=1, description="Measurable outcomes")
    safety_constraints: List[str] = Field(default_factory=list, description="Safety invariants")
    budget: float = Field(..., ge=0, description="Cost or resource budget allocated")
    evaluation_policy: str = Field(..., min_length=1, description="Declared evaluation policy to prevent optional-stopping")
    requires_controls: bool = Field(True, description="Flag indicating if controls are mandatory for this design")
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

    @model_validator(mode='after')
    def check_design_validity(self):
        if self.requires_controls and not self.controls:
            raise ValueError("Controls are required for this experiment design but none were provided.")
        if not self.metrics:
            raise ValueError("Experiment design must have at least one measurable metric.")
        return self

class Observation(BaseModel):
    model_config = {"frozen": True}

    id: str = Field(..., description="Unique identifier for the observation")
    experiment_id: str = Field(..., description="Experiment design this observation belongs to")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    metrics_recorded: Dict[str, float] = Field(..., description="Actual recorded metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EvaluationResult(BaseModel):
    model_config = {"frozen": True}

    id: str = Field(..., description="Unique identifier for the evaluation")
    experiment_id: str = Field(..., description="Experiment evaluated")
    policy_version: str = Field(..., description="Evaluation policy used")
    is_successful: bool = Field(..., description="Whether the hypothesis was supported")
    is_null: bool = Field(False, description="Whether the result was null/inconclusive")
    is_negative: bool = Field(False, description="Whether the result actively contradicted the hypothesis")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Statistical output (e.g. p-value, effect size)")
    reasoning: str = Field(..., min_length=1, description="Why this conclusion was reached")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

class BeliefUpdateRecord(BaseModel):
    model_config = {"frozen": True}

    id: str = Field(..., description="Unique identifier for this belief update proposal")
    hypothesis_id: str = Field(..., description="Hypothesis ID this relates to")
    experiment_id: str = Field(..., description="Experiment ID providing evidence")
    policy_version: str = Field(..., description="Policy version used in evaluation")
    proposed_belief_shift: str = Field(..., min_length=1, description="Description of how belief should change")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

class ReproducibilityBundle(BaseModel):
    model_config = {"frozen": True}

    experiment_id: str
    hypothesis: Hypothesis
    design: ExperimentDesign
    observations: List[Observation]
    evaluation: Optional[EvaluationResult]
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
