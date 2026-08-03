from typing import Dict, Any, List, Tuple
from gabriel_engine.learning.models import ProcedureCandidate, FailurePreventionRule

class LessonExtractor:
    """
    Extracts potential lesson candidates and failure prevention rules from normalized outcomes.
    """
    def extract_candidates(self, normalized_outcome: Dict[str, Any]) -> Tuple[List[ProcedureCandidate], List[FailurePreventionRule]]:
        """
        Analyzes a normalized outcome and returns potential procedure candidates and failure rules.
        """
        candidates = []
        rules = []

        event_type = normalized_outcome.get("event_type", "")
        success = normalized_outcome.get("success", False)
        ingest_id = str(normalized_outcome.get("ingest_id", ""))

        if success and ("code_review" in event_type or "project_assimilation" in event_type):
            candidates.append(
                ProcedureCandidate(
                    procedure_id=f"PROC-AUTO-{ingest_id}",
                    name=f"Generated from successful {event_type}",
                    applies_when={"task_type": event_type},
                    recommended_action=[f"Replicate conditions of {ingest_id}"],
                    status="CANDIDATE",
                    last_reviewed="2024-01-01",
                    evidence_ids=[ingest_id]
                )
            )

        if not success:
            rules.append(
                FailurePreventionRule(
                    rule_id=f"RULE-PREVENT-{ingest_id}",
                    description=f"Prevent failure pattern observed in {event_type}",
                    condition={"event_type": event_type},
                    preventative_action="Halt and review before proceeding",
                    status="ADVISORY"
                )
            )

        return candidates, rules
