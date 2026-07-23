import datetime
import uuid
import re
from typing import List, Dict, Any, Optional

# Supported card types
SUPPORTED_CARD_TYPES = {
    "KNOWLEDGE",
    "LESSON",
    "FAILURE",
    "REPAIR",
    "DECISION",
    "SKILL"
}

# Validation states
VALIDATION_STATES = {
    "UNVALIDATED",
    "VALID",
    "INVALID"
}

# Card statuses
CARD_STATUSES = {
    "DRAFT",
    "REVIEWED",
    "APPROVED",
    "ACTIVE",
    "DEPRECATED"
}

class ValidationError(Exception):
    pass

class KnowledgeCard:
    def __init__(
        self,
        card_id: str,
        card_type: str,
        schema_version: str,
        title: str,
        summary: str,
        body: str,
        status: str,
        confidence: float,
        validation_state: str,
        created_at: str,
        updated_at: str,
        created_by: str,
        source_type: str,
        source_ids: List[str],
        parent_card_ids: List[str],
        related_card_ids: List[str],
        tags: List[str],
        security_classification: str,
        evidence: str,
        supersedes: Optional[str] = None,
        superseded_by: Optional[str] = None,
        # "Why does this exist?" fields
        why_created: str = "",
        problem_solved: str = "",
        future_work_dependent: str = "",
        embedding: Optional[List[float]] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        self.card_id = card_id
        self.card_type = card_type
        self.schema_version = schema_version
        self.title = title
        self.summary = summary
        self.body = body
        self.status = status
        self.confidence = confidence
        self.validation_state = validation_state
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.source_type = source_type
        self.source_ids = source_ids or []
        self.parent_card_ids = parent_card_ids or []
        self.related_card_ids = related_card_ids or []
        self.tags = tags or []
        self.security_classification = security_classification
        self.evidence = evidence
        self.supersedes = supersedes
        self.superseded_by = superseded_by
        self.why_created = why_created
        self.problem_solved = problem_solved
        self.future_work_dependent = future_work_dependent
        self.embedding = embedding or []
        self.extra_metadata = extra_metadata or {}

        self.validate()

    def validate(self) -> None:
        """Validates all fields of the card model."""
        if not self.card_id:
            raise ValidationError("card_id is required")
        if self.card_type not in SUPPORTED_CARD_TYPES:
            raise ValidationError(f"card_type must be one of {SUPPORTED_CARD_TYPES}")
        if not self.schema_version:
            raise ValidationError("schema_version is required")
        if not self.title or not self.title.strip():
            raise ValidationError("title is required and cannot be empty")
        if not self.summary or not self.summary.strip():
            raise ValidationError("summary is required")
        if not self.body or not self.body.strip():
            raise ValidationError("body is required")
        if self.status not in CARD_STATUSES:
            raise ValidationError(f"status must be one of {CARD_STATUSES}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValidationError("confidence must be a float between 0.0 and 1.0")
        if self.validation_state not in VALIDATION_STATES:
            raise ValidationError(f"validation_state must be one of {VALIDATION_STATES}")
        if not self.created_at:
            raise ValidationError("created_at is required")
        if not self.updated_at:
            raise ValidationError("updated_at is required")
        if not self.created_by:
            raise ValidationError("created_by is required")
        if not self.security_classification:
            raise ValidationError("security_classification is required")
        if not self.evidence or not self.evidence.strip():
            raise ValidationError("evidence is required and cannot be empty")

        # Validate ISO 8601 timestamps safely
        for ts_name, ts_val in [("created_at", self.created_at), ("updated_at", self.updated_at)]:
            try:
                val_to_parse = ts_val
                if val_to_parse.endswith("Z"):
                    val_to_parse = val_to_parse[:-1] + "+00:00"
                datetime.datetime.fromisoformat(val_to_parse)
            except Exception as e:
                raise ValidationError(f"Field {ts_name} is not a valid ISO 8601 string: {e}")

        # Ensure "Why does this exist?" fields are valid strings
        if not isinstance(self.why_created, str):
            raise ValidationError("why_created must be a string")
        if not isinstance(self.problem_solved, str):
            raise ValidationError("problem_solved must be a string")
        if not isinstance(self.future_work_dependent, str):
            raise ValidationError("future_work_dependent must be a string")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the card instance to a dictionary."""
        return {
            "card_id": self.card_id,
            "card_type": self.card_type,
            "schema_version": self.schema_version,
            "title": self.title,
            "summary": self.summary,
            "body": self.body,
            "status": self.status,
            "confidence": self.confidence,
            "validation_state": self.validation_state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "source_type": self.source_type,
            "source_ids": self.source_ids,
            "parent_card_ids": self.parent_card_ids,
            "related_card_ids": self.related_card_ids,
            "tags": self.tags,
            "security_classification": self.security_classification,
            "evidence": self.evidence,
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "why_created": self.why_created,
            "problem_solved": self.problem_solved,
            "future_work_dependent": self.future_work_dependent,
            "embedding": self.embedding,
            "extra_metadata": self.extra_metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeCard":
        """Deserializes a dictionary into a KnowledgeCard instance."""
        return cls(
            card_id=data.get("card_id"),
            card_type=data.get("card_type"),
            schema_version=data.get("schema_version"),
            title=data.get("title"),
            summary=data.get("summary"),
            body=data.get("body"),
            status=data.get("status"),
            confidence=data.get("confidence"),
            validation_state=data.get("validation_state"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            created_by=data.get("created_by"),
            source_type=data.get("source_type"),
            source_ids=data.get("source_ids"),
            parent_card_ids=data.get("parent_card_ids"),
            related_card_ids=data.get("related_card_ids"),
            tags=data.get("tags"),
            security_classification=data.get("security_classification"),
            evidence=data.get("evidence"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            why_created=data.get("why_created", ""),
            problem_solved=data.get("problem_solved", ""),
            future_work_dependent=data.get("future_work_dependent", ""),
            embedding=data.get("embedding", []),
            extra_metadata=data.get("extra_metadata")
        )
