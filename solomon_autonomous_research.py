"""
Solomon SOSS Phase 7: Autonomous Research & Proactive Evaluation

This module initiates research projects independently (such as evaluating the performance of
different mathematical solvers, sports databases, or parsing schemas) to proactively
promote validated winners and safely archive low-performing losers.
"""

import time
from typing import List, Dict, Any, Tuple


class ResearchCandidate:
    """
    Represents a candidate capability evaluated during proactive research.
    """
    def __init__(self, name: str, code_implementation: str, expected_latency_ms: float, accuracy: float):
        self.name = name
        self.code_implementation = code_implementation
        self.expected_latency_ms = expected_latency_ms
        self.accuracy = accuracy


class AutonomousResearcher:
    """
    Initiates independent research evaluations, comparing candidate options
    to identify, promote, or archive functional capabilities.
    """
    def __init__(self):
        self.completed_research_projects: List[Dict[str, Any]] = []

    def conduct_comparative_research(
        self,
        project_name: str,
        candidates: List[ResearchCandidate]
    ) -> Dict[str, Any]:
        """
        Proactively evaluates a list of ResearchCandidates based on utility scoring:
        Utility = w_a * Accuracy - w_l * Latency
        Identify the winning candidate to promote, and archive the remaining candidates.
        """
        if not candidates:
            raise ValueError("Research comparative evaluation requires at least one candidate.")

        scored_candidates = []
        w_a = 100.0 # Weight for accuracy
        w_l = 0.5   # Penalty weight for latency (ms)

        for cand in candidates:
            # Score formula
            score = (w_a * cand.accuracy) - (w_l * cand.expected_latency_ms)
            scored_candidates.append({
                "candidate": cand,
                "score": round(score, 2)
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        winner = scored_candidates[0]["candidate"]
        winner_score = scored_candidates[0]["score"]

        losers = [item["candidate"] for item in scored_candidates[1:]]

        # Compile research report
        report = {
            "project_name": project_name,
            "evaluation_timestamp": int(time.time()),
            "winner": {
                "name": winner.name,
                "score": winner_score,
                "accuracy": winner.accuracy,
                "latency_ms": winner.expected_latency_ms
            },
            "archived_losers": [
                {
                    "name": l.name,
                    "accuracy": l.accuracy,
                    "latency_ms": l.expected_latency_ms
                }
                for l in losers
            ],
            "decision": f"PROMOTE '{winner.name}' to active SOK cards. ARCHIVE remaining {len(losers)} candidate options."
        }

        self.completed_research_projects.append(report)
        return report
