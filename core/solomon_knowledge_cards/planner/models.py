import datetime
from typing import List, Dict, Any, Optional

class TaskPlan:
    def __init__(
        self,
        plan_id: str,
        task_id: str,
        objective: str,
        steps: List[Dict[str, Any]],
        retrieved_memory_card_ids: List[str],
        injected_safeguards: List[Dict[str, Any]],
        status: str = "DRAFT",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.plan_id = plan_id
        self.task_id = task_id
        self.objective = objective
        self.steps = steps or []
        self.retrieved_memory_card_ids = retrieved_memory_card_ids or []
        self.injected_safeguards = injected_safeguards or []
        self.status = status
        self.created_at = created_at or datetime.datetime.now(datetime.UTC).isoformat()
        self.updated_at = updated_at or self.created_at

    def validate(self) -> None:
        """Validates standard structure constraints on the TaskPlan."""
        if not self.plan_id:
            raise ValueError("plan_id is required")
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.objective or not self.objective.strip():
            raise ValueError("objective is required")
        if self.status not in ("DRAFT", "APPROVED", "EXECUTED", "FAILED"):
            raise ValueError(f"Invalid plan status: {self.status}")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the task plan to a dictionary."""
        return {
            "plan_id": self.plan_id,
            "task_id": self.task_id,
            "objective": self.objective,
            "steps": self.steps,
            "retrieved_memory_card_ids": self.retrieved_memory_card_ids,
            "injected_safeguards": self.injected_safeguards,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskPlan":
        """Deserializes a dictionary into a TaskPlan instance."""
        return cls(
            plan_id=data.get("plan_id"),
            task_id=data.get("task_id"),
            objective=data.get("objective"),
            steps=data.get("steps", []),
            retrieved_memory_card_ids=data.get("retrieved_memory_card_ids", []),
            injected_safeguards=data.get("injected_safeguards", []),
            status=data.get("status", "DRAFT"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
