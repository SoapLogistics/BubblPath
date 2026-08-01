import datetime
import hashlib
from typing import List, Dict, Any, Optional

CLASSIFICATION_TYPES = {
    "DIRECT",
    "TEMPORAL",
    "SCOPED",
    "NUMERICAL",
    "DEFINITIONAL",
    "SOURCE_QUALITY",
    "APPARENT_NON_CONFLICT"
}

RESOLUTION_ACTIONS = {
    "RETAIN_BOTH_WITH_SCOPE",
    "LOWER_CONFIDENCE",
    "REQUEST_EVIDENCE",
    "SUPERSEDE",
    "MERGE_DEFINITIONS",
    "REJECT_NEW_CLAIM"
}

class ValidationError(Exception):
    pass

def _parse_iso_date(date_str: Optional[str]) -> Optional[datetime.datetime]:
    if not date_str:
        return None
    try:
        val = date_str
        if val.endswith("Z"):
            val = val[:-1] + "+00:00"
        return datetime.datetime.fromisoformat(val)
    except Exception as e:
        raise ValidationError(f"Invalid ISO 8601 string: {date_str} - {e}")

class ClaimScope:
    def __init__(self, start_time: Optional[str] = None, end_time: Optional[str] = None,
                 geospatial: Optional[str] = None, context: Optional[str] = None):
        self.start_time = start_time
        self.end_time = end_time
        self.geospatial = geospatial
        self.context = context
        self.validate()

    def validate(self):
        _parse_iso_date(self.start_time)
        _parse_iso_date(self.end_time)

    def to_dict(self):
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "geospatial": self.geospatial,
            "context": self.context
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if not data:
            return cls()
        return cls(**data)

    def is_disjoint_temporal(self, other: 'ClaimScope') -> bool:
        if not self.start_time and not self.end_time: return False
        if not other.start_time and not other.end_time: return False

        t1_start = _parse_iso_date(self.start_time)
        t1_end = _parse_iso_date(self.end_time)
        t2_start = _parse_iso_date(other.start_time)
        t2_end = _parse_iso_date(other.end_time)

        if t1_end and t2_start and t1_end < t2_start:
            return True
        if t2_end and t1_start and t2_end < t1_start:
            return True

        return False

    def is_disjoint_geospatial(self, other: 'ClaimScope') -> bool:
        if self.geospatial and other.geospatial and self.geospatial != other.geospatial:
            return True
        return False

    def is_disjoint_context(self, other: 'ClaimScope') -> bool:
        if self.context and other.context and self.context != other.context:
            return True
        return False

class Claim:
    def __init__(self, claim_id: str, entity: str, predicate: str, object_value: str,
                 unit: Optional[str] = None, qualifier: Optional[str] = None,
                 scope: Optional[ClaimScope] = None):
        self.claim_id = claim_id
        self.entity = entity.strip().lower()
        self.predicate = predicate.strip().lower()
        self.object_value = object_value.strip().lower()
        self.unit = unit.strip().lower() if unit else None
        self.qualifier = qualifier.strip().lower() if qualifier else None
        self.scope = scope or ClaimScope()
        self.validate()

    def validate(self):
        if not self.claim_id:
            raise ValidationError("claim_id is required")
        if not self.entity:
            raise ValidationError("entity is required")
        if not self.predicate:
            raise ValidationError("predicate is required")
        if not self.object_value:
            raise ValidationError("object_value is required")

    def to_dict(self):
        return {
            "claim_id": self.claim_id,
            "entity": self.entity,
            "predicate": self.predicate,
            "object_value": self.object_value,
            "unit": self.unit,
            "qualifier": self.qualifier,
            "scope": self.scope.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        data_copy = data.copy()
        if "scope" in data_copy and isinstance(data_copy["scope"], dict):
            data_copy["scope"] = ClaimScope.from_dict(data_copy["scope"])
        return cls(**data_copy)

    def fingerprint(self) -> str:
        core = f"{self.entity}|{self.predicate}|{self.object_value}|{self.unit or ''}|{self.qualifier or ''}"
        return hashlib.sha256(core.encode('utf-8')).hexdigest()

    def topic_fingerprint(self) -> str:
        core = f"{self.entity}|{self.predicate}"
        return hashlib.sha256(core.encode('utf-8')).hexdigest()

class ContradictionEvidence:
    def __init__(self, source_id: str, confidence: float, timestamp: str, source_quality: float = 1.0):
        self.source_id = source_id
        self.confidence = confidence
        self.timestamp = timestamp
        self.source_quality = source_quality
        self.validate()

    def validate(self):
        if not self.source_id:
            raise ValidationError("source_id is required")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValidationError("confidence must be between 0.0 and 1.0")
        if not (0.0 <= self.source_quality <= 1.0):
            raise ValidationError("source_quality must be between 0.0 and 1.0")
        _parse_iso_date(self.timestamp)

    def to_dict(self):
        return {
            "source_id": self.source_id,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "source_quality": self.source_quality
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

class ResolutionProposal:
    def __init__(self, action: str, reason_code: str, details: Dict[str, Any]):
        self.action = action
        self.reason_code = reason_code
        self.details = details
        self.validate()

    def validate(self):
        if self.action not in RESOLUTION_ACTIONS:
            raise ValidationError(f"Invalid action: {self.action}")
        if not self.reason_code:
            raise ValidationError("reason_code is required")

    def to_dict(self):
        return {
            "action": self.action,
            "reason_code": self.reason_code,
            "details": self.details
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

class ContradictionCase:
    def __init__(self, case_id: str, claim1: Claim, claim2: Claim,
                 evidence1: ContradictionEvidence, evidence2: ContradictionEvidence,
                 classification: str = "APPARENT_NON_CONFLICT",
                 severity: float = 0.0, uncertainty: float = 0.0,
                 proposals: Optional[List[ResolutionProposal]] = None,
                 status: str = "OPEN"):
        self.case_id = case_id
        self.claim1 = claim1
        self.claim2 = claim2
        self.evidence1 = evidence1
        self.evidence2 = evidence2
        self.classification = classification
        self.severity = severity
        self.uncertainty = uncertainty
        self.proposals = proposals or []
        self.status = status
        self.validate()

    def validate(self):
        if not self.case_id:
            raise ValidationError("case_id is required")
        self.claim1.validate()
        self.claim2.validate()
        self.evidence1.validate()
        self.evidence2.validate()
        if self.classification not in CLASSIFICATION_TYPES:
            raise ValidationError(f"Invalid classification: {self.classification}")
        if not (0.0 <= self.severity <= 1.0):
            raise ValidationError("severity must be between 0.0 and 1.0")
        if not (0.0 <= self.uncertainty <= 1.0):
            raise ValidationError("uncertainty must be between 0.0 and 1.0")
        for p in self.proposals:
            p.validate()

    def generate_fingerprint(self) -> str:
        fp1 = self.claim1.fingerprint()
        fp2 = self.claim2.fingerprint()
        fps = sorted([fp1, fp2])
        return hashlib.sha256(f"{fps[0]}|{fps[1]}".encode('utf-8')).hexdigest()

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "claim1": self.claim1.to_dict(),
            "claim2": self.claim2.to_dict(),
            "evidence1": self.evidence1.to_dict(),
            "evidence2": self.evidence2.to_dict(),
            "classification": self.classification,
            "severity": self.severity,
            "uncertainty": self.uncertainty,
            "proposals": [p.to_dict() for p in self.proposals],
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        data_copy = data.copy()
        data_copy["claim1"] = Claim.from_dict(data_copy["claim1"])
        data_copy["claim2"] = Claim.from_dict(data_copy["claim2"])
        data_copy["evidence1"] = ContradictionEvidence.from_dict(data_copy["evidence1"])
        data_copy["evidence2"] = ContradictionEvidence.from_dict(data_copy["evidence2"])
        if "proposals" in data_copy:
            data_copy["proposals"] = [ResolutionProposal.from_dict(p) for p in data_copy["proposals"]]
        return cls(**data_copy)

class ResolutionPolicy:
    def __init__(self, numerical_tolerance: float = 0.05,
                 temporal_strictness: bool = True,
                 source_quality_threshold: float = 0.5):
        self.numerical_tolerance = numerical_tolerance
        self.temporal_strictness = temporal_strictness
        self.source_quality_threshold = source_quality_threshold
