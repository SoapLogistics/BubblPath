import datetime
from typing import List, Optional, Dict, Any

class CardType:
    KNOWLEDGE = "KNOWLEDGE"
    LESSON = "LESSON"
    FAILURE = "FAILURE"
    REPAIR = "REPAIR"
    DECISION = "DECISION"
    SKILL = "SKILL"
    PROCEDURE = "PROCEDURE"

    ALL_TYPES = [KNOWLEDGE, LESSON, FAILURE, REPAIR, DECISION, SKILL, PROCEDURE]

class CardStatus:
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

    ALL_STATUSES = [DRAFT, REVIEWED, APPROVED, ACTIVE, DEPRECATED, ARCHIVED]

class ValidationState:
    PENDING = "PENDING"
    SYSTEM_VALIDATED = "SYSTEM"
    HUMAN_VALIDATED = "HUMAN"
    LLM_EVAL = "LLM_EVAL"
    REJECTED = "REJECTED"

    ALL_STATES = [PENDING, SYSTEM_VALIDATED, HUMAN_VALIDATED, LLM_EVAL, REJECTED]

class CardRelation:
    PREVENTS = "PREVENTS"
    ENHANCES = "ENHANCES"
    DEPENDS_ON = "DEPENDS_ON"
    SUPERSEDES = "SUPERSEDES"
    PROPOSES_UPDATE_TO = "PROPOSES_UPDATE_TO"
    RELATED_TO = "RELATED_TO"

    ALL_RELATIONS = [PREVENTS, ENHANCES, DEPENDS_ON, SUPERSEDES, PROPOSES_UPDATE_TO, RELATED_TO]

class KnowledgeCardModel:
    def __init__(
        self,
        card_id: str,
        card_type: str,
        title: str,
        summary: str,
        body: str,
        schema_version: str = "1.0.0",
        status: str = CardStatus.DRAFT,
        confidence: float = 0.5,
        validation_state: str = ValidationState.PENDING,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        created_by: str = "SYSTEM",
        source_type: str = "MANUAL",
        source_ids: Optional[List[str]] = None,
        parent_card_ids: Optional[List[str]] = None,
        related_card_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        security_classification: str = "INTERNAL",
        evidence: Optional[str] = None,
        supersedes: Optional[str] = None,
        superseded_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        why_created: Optional[str] = None,
        problem_solved: Optional[str] = None,
        future_work_dependent: Optional[str] = None
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

        now = datetime.datetime.utcnow().isoformat() + "Z"
        self.created_at = created_at or now
        self.updated_at = updated_at or now

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
        self.metadata = metadata or {}
        self.why_created = why_created
        self.problem_solved = problem_solved
        self.future_work_dependent = future_work_dependent

    def validate(self) -> None:
        """Enforces schema structural integrity and validation rules."""
        if not self.card_id or not isinstance(self.card_id, str):
            raise ValueError("Invalid card_id: Must be a non-empty string.")
        if self.card_type not in CardType.ALL_TYPES:
            raise ValueError(f"Invalid card_type: Must be one of {CardType.ALL_TYPES}.")
        if self.status not in CardStatus.ALL_STATUSES:
            raise ValueError(f"Invalid status: Must be one of {CardStatus.ALL_STATUSES}.")
        if self.validation_state not in ValidationState.ALL_STATES:
            raise ValueError(f"Invalid validation_state: Must be one of {ValidationState.ALL_STATES}.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be a float between 0.0 and 1.0.")
        if not self.title or not isinstance(self.title, str):
            raise ValueError("Title must be a non-empty string.")
        if not isinstance(self.source_ids, list):
            raise ValueError("source_ids must be a list of strings.")
        if not isinstance(self.parent_card_ids, list):
            raise ValueError("parent_card_ids must be a list of strings.")
        if not isinstance(self.related_card_ids, list):
            raise ValueError("related_card_ids must be a list of strings.")
        if not isinstance(self.tags, list):
            raise ValueError("tags must be a list of strings.")

    def to_dict(self) -> Dict[str, Any]:
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
            "metadata": self.metadata,
            "why_created": self.why_created,
            "problem_solved": self.problem_solved,
            "future_work_dependent": self.future_work_dependent
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeCardModel":
        return cls(
            card_id=data.get("card_id", ""),
            card_type=data.get("card_type", ""),
            schema_version=data.get("schema_version", "1.0.0"),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            body=data.get("body", ""),
            status=data.get("status", CardStatus.DRAFT),
            confidence=float(data.get("confidence", 0.5)),
            validation_state=data.get("validation_state", ValidationState.PENDING),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            created_by=data.get("created_by", "SYSTEM"),
            source_type=data.get("source_type", "MANUAL"),
            source_ids=data.get("source_ids"),
            parent_card_ids=data.get("parent_card_ids"),
            related_card_ids=data.get("related_card_ids"),
            tags=data.get("tags"),
            security_classification=data.get("security_classification", "INTERNAL"),
            evidence=data.get("evidence"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            metadata=data.get("metadata"),
            why_created=data.get("why_created"),
            problem_solved=data.get("problem_solved"),
            future_work_dependent=data.get("future_work_dependent")
        )
