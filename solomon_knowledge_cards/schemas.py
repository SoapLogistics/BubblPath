from typing import Dict, Any, List

def validate_worker_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a Worker Report dictionary against the canonical schema.
    Raises ValueError if invalid, otherwise returns the validated and cleaned dictionary.
    """
    required_keys = ["report_id", "task_id", "outcome"]
    for key in required_keys:
        if key not in report or not report[key]:
            raise ValueError(f"Worker Report is missing required key: {key}")

    outcome = str(report["outcome"]).upper()
    valid_outcomes = ["SUCCESS", "PARTIAL", "FAILURE", "BLOCKED"]
    if outcome not in valid_outcomes:
        raise ValueError(f"Invalid outcome: {outcome}. Must be one of {valid_outcomes}")

    classification = str(report.get("security_classification", "INTERNAL")).upper()
    valid_classifications = ["PUBLIC", "INTERNAL", "RESTRICTED"]
    if classification not in valid_classifications:
        raise ValueError(f"Invalid security_classification: {classification}")

    procedure_ids = report.get("procedure_ids", [])
    if not isinstance(procedure_ids, list):
        raise ValueError("procedure_ids must be a list of strings")

    evidence = report.get("evidence", [])
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list of objects")

    changed_files = report.get("changed_files")
    if changed_files is not None and not isinstance(changed_files, list):
        raise ValueError("changed_files must be a list of strings")

    test_results = report.get("test_results")
    if test_results is not None and not isinstance(test_results, dict):
        raise ValueError("test_results must be a dictionary")

    # Support an optional generic metadata dictionary for other domains
    metadata = report.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")

    # Return sanitized / normalized dict
    return {
        "report_id": str(report["report_id"]),
        "task_id": str(report["task_id"]),
        "procedure_ids": [str(pid) for pid in procedure_ids],
        "worker_id": str(report.get("worker_id", "generic-worker")),
        "worker_type": str(report.get("worker_type", "GENERIC")),
        "started_at": str(report.get("started_at", "")),
        "completed_at": str(report.get("completed_at", "")),
        "outcome": outcome,
        "attempted": str(report.get("attempted", "")),
        "succeeded": str(report.get("succeeded", "")),
        "failed": str(report.get("failed", "")),
        "root_cause": report.get("root_cause"),
        "repair_action": report.get("repair_action"),
        "evidence": evidence,
        "changed_files": [str(f) for f in changed_files] if changed_files is not None else [],
        "test_results": test_results if test_results is not None else {},
        "metadata": metadata,
        "security_classification": classification,
        "candidate_learning": bool(report.get("candidate_learning", True))
    }


def validate_review_payload(review: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates an SS3 Review payload dictionary.
    Raises ValueError if invalid, otherwise returns the validated and cleaned dictionary.
    """
    required_keys = ["card_id", "reviewer", "decision"]
    for key in required_keys:
        if key not in review or not review[key]:
            raise ValueError(f"Review payload is missing required key: {key}")

    decision = str(review["decision"]).upper()
    valid_decisions = ["REVIEW", "APPROVE", "ACTIVATE", "REJECT", "DEPRECATE"]
    if decision not in valid_decisions:
        raise ValueError(f"Invalid decision: {decision}. Must be one of {valid_decisions}")

    # Rejection requires reason
    if decision == "REJECT" and not review.get("reason"):
        raise ValueError("A rejection decision requires a reason.")

    # Return sanitized / normalized dict
    return {
        "card_id": str(review["card_id"]),
        "reviewer": str(review["reviewer"]),
        "decision": decision,
        "notes": review.get("notes"),
        "reason": review.get("reason"),
        "evidence_checked": bool(review.get("evidence_checked", False)),
        "confidence": float(review.get("confidence", 0.0))
    }
