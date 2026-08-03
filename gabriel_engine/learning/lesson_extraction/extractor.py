from typing import Dict, Any, List

class LessonCandidateExtractor:
    """Extracts proposed procedures, agent profiles, and failure prevention rules from normalized data."""
    def extract_candidates(self, normalized_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidates = []
        failures = [r for r in normalized_records if not r.get("success")]
        successes = [r for r in normalized_records if r.get("success")]

        # Simple extraction rule: If we see a failure and a subsequent success for the same task, propose a procedure.
        if failures:
            candidates.append({
                "type": "failure_prevention_rule",
                "trigger": failures[0]["context"].get("task_type", "unknown"),
                "suggestion": "Require deeper integration tests before merge."
            })

        for s in successes:
            candidates.append({
                "type": "agent_performance_profile",
                "agent": s["agent"],
                "score_bump": 1.0,
                "task_type": s["context"].get("task_type", "unknown")
            })

        return candidates
