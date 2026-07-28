from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass
class ConflictCard:
    conflict_id: str
    topic: str
    claim_a: Dict[str, Any]
    claim_b: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    confidence: float
    suggested_research: str
    status: str = "OPEN"
    created_at: float = field(default_factory=time.time)

@dataclass
class ConsensusNode:
    consensus_id: str
    topic: str
    statement: str
    supporting_sources: List[str]
    opposing_sources: List[str]
    confidence: float
    created_at: float = field(default_factory=time.time)

@dataclass
class ResearchCampaign:
    campaign_id: str
    question: str
    known_evidence: List[str]
    conflicting_evidence: List[str]
    missing_information: str
    status: str = "OPEN"
    created_at: float = field(default_factory=time.time)
