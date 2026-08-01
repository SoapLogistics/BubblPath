import dataclasses
import time
from typing import Any, Dict, List, Optional

@dataclasses.dataclass
class ClaimScope:
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    domain: Optional[str] = None
    confidence: float = 1.0
    tags: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

@dataclasses.dataclass
class Claim:
    id: str
    entity: str
    predicate: str
    value: Any
    source_id: str
    timestamp: float
    scope: ClaimScope = dataclasses.field(default_factory=ClaimScope)
    qualifiers: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d['scope'] = self.scope.to_dict()
        return d

@dataclasses.dataclass
class ContradictionEvidence:
    claim_a: Claim
    claim_b: Claim

    def to_dict(self) -> Dict[str, Any]:
        return {
            'claim_a': self.claim_a.to_dict(),
            'claim_b': self.claim_b.to_dict()
        }

@dataclasses.dataclass
class ResolutionPolicy:
    weight_source_quality: float = 1.0
    weight_recency: float = 1.0
    require_manual_review_threshold: float = 0.8
    numerical_tolerance: float = 0.01

@dataclasses.dataclass
class ResolutionProposal:
    action: str  # e.g. "retain-both-with-scope", "lower-confidence", "request-evidence", "supersede", "merge-definitions", "reject-new"
    reason_code: str
    explanation: str
    confidence: float
    affected_claim_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

@dataclasses.dataclass
class ContradictionCase:
    id: str
    classification: str  # "direct", "temporal", "scoped", "numerical", "definitional", "source-quality", "apparent/non-conflict"
    severity: float
    priority_score: float
    evidence: ContradictionEvidence
    proposals: List[ResolutionProposal]
    status: str = "OPEN"  # "OPEN", "REVIEW", "RESOLVED"
    created_at: float = dataclasses.field(default_factory=time.time)
    updated_at: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'classification': self.classification,
            'severity': self.severity,
            'priority_score': self.priority_score,
            'evidence': self.evidence.to_dict(),
            'proposals': [p.to_dict() for p in self.proposals],
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
